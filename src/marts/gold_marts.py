from __future__ import annotations
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, countDistinct, count, sum as fsum, avg, when, lit, current_timestamp, expr
from src.common.config import CatalogConfig
from src.common.logging_utils import get_logger

logger = get_logger(__name__)

def build_content_daily_kpis(spark: SparkSession, c: CatalogConfig) -> None:
    playback = spark.table(c.t(c.silver, "fact_playback"))
    ads = spark.table(c.t(c.silver, "fact_ad_events"))
    social = spark.table(c.t(c.silver, "fact_social_signals"))
    content = spark.table(c.t(c.silver, "dim_content"))

    views = (playback.filter(col("event_type")=="PLAY")
             .groupBy(col("event_date").alias("kpi_date"), "content_id")
             .agg(
                count("*").alias("views"),
                countDistinct("user_id").alias("unique_viewers"),
                fsum(when(col("watch_time_sec").isNull(),0).otherwise(col("watch_time_sec"))).alias("watch_time_sec"),
                avg("watch_time_sec").alias("avg_watch_time_sec"),
             ))

    completion = (playback.filter(col("event_type")=="COMPLETE")
                  .groupBy(col("event_date").alias("kpi_date"), "content_id")
                  .agg(count("*").alias("completion_events")))

    adk = (ads.groupBy(col("event_date").alias("kpi_date"), "content_id")
           .agg(
               fsum(when(col("event_type")=="IMPRESSION",1).otherwise(0)).alias("ad_impressions"),
               fsum(when(col("event_type")=="CLICK",1).otherwise(0)).alias("ad_clicks"),
               fsum(col("revenue_usd")).alias("ad_revenue_usd"),
           ))

    sent = (social.groupBy(col("mention_date").alias("kpi_date"), "content_id")
            .agg(avg("sentiment").alias("sentiment_avg")))

    out = (views.join(completion, ["kpi_date","content_id"], "left")
           .join(adk, ["kpi_date","content_id"], "left")
           .join(sent, ["kpi_date","content_id"], "left")
           .join(content.select("content_id","genre","content_type"), "content_id", "left")
           .fillna({"completion_events":0, "ad_impressions":0, "ad_clicks":0})
           .withColumn("completion_rate", when(col("views")>0, col("completion_events")/col("views")).otherwise(lit(0.0)))
           .withColumn("ctr", when(col("ad_impressions")>0, col("ad_clicks")/col("ad_impressions")).otherwise(lit(0.0)))
           .withColumn("ingestion_timestamp", current_timestamp()))
    out.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.gold, "content_daily_kpis"))
    logger.info("gold.content_daily_kpis built")

def build_audience_daily_engagement(spark: SparkSession, c: CatalogConfig) -> None:
    sess = spark.table(c.t(c.silver, "fact_sessions"))
    geo = spark.table(c.t(c.silver, "dim_geo"))
    plat = spark.table(c.t(c.silver, "dim_platform"))
    dev = spark.table(c.t(c.silver, "dim_device"))

    joined = (sess.join(geo.select("geo_key","country","region"), "geo_key", "left")
              .join(plat.select("platform_key","platform"), "platform_key", "left")
              .join(dev.select("device_key","device_type"), "device_key", "left"))

    out = (joined.groupBy(col("session_date").alias("kpi_date"), "country","region","platform","device_type")
           .agg(
              countDistinct("user_id").alias("dau"),
              countDistinct("session_id").alias("sessions"),
              avg("total_watch_time_sec").alias("avg_session_watch_time_sec"),
              avg("total_events").alias("avg_events_per_session"),
           )
           .withColumn("ingestion_timestamp", current_timestamp()))
    out.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.gold, "audience_daily_engagement"))
    logger.info("gold.audience_daily_engagement built")

def build_subscription_daily_summary(spark: SparkSession, c: CatalogConfig) -> None:
    subs = spark.table(c.t(c.silver, "dim_subscription"))
    # Intermediate approach: derive counts from start/end + status, no SCD2
    today = expr("current_date()").cast("date")
    active = subs.filter(col("status")=="active").groupBy(lit(None).cast("date").alias("kpi_date"), "plan_name")                .agg(countDistinct("subscription_id").alias("active_subscriptions"))
    new_subs = subs.filter(col("start_date") >= expr("date_sub(current_date(), 1)")).groupBy(lit(None).cast("date").alias("kpi_date"), "plan_name")                .agg(countDistinct("subscription_id").alias("new_subscriptions"))
    cancels = subs.filter((col("status")=="canceled") & (col("end_date") >= expr("date_sub(current_date(), 1)"))).groupBy(lit(None).cast("date").alias("kpi_date"), "plan_name")                .agg(countDistinct("subscription_id").alias("cancellations"))

    out = (active.join(new_subs, ["kpi_date","plan_name"], "left")
           .join(cancels, ["kpi_date","plan_name"], "left")
           .fillna({"new_subscriptions":0, "cancellations":0})
           .withColumn("kpi_date", expr("current_date()").cast("date"))
           .withColumn("ingestion_timestamp", current_timestamp()))
    out.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.gold, "subscription_daily_summary"))
    logger.info("gold.subscription_daily_summary built")

def build_ad_daily_yield(spark: SparkSession, c: CatalogConfig) -> None:
    ads = spark.table(c.t(c.silver, "fact_ad_events"))
    out = (ads.groupBy(col("event_date").alias("kpi_date"), "campaign_id","placement","ad_format")
           .agg(
              fsum(when(col("event_type")=="IMPRESSION",1).otherwise(0)).alias("impressions"),
              fsum(when(col("event_type")=="CLICK",1).otherwise(0)).alias("clicks"),
              fsum(col("revenue_usd")).alias("revenue_usd"),
           )
           .withColumn("ctr", when(col("impressions")>0, col("clicks")/col("impressions")).otherwise(lit(0.0)))
           .withColumn("rpm", when(col("impressions")>0, (col("revenue_usd")*1000)/col("impressions")).otherwise(lit(0.0)))
           .withColumn("ingestion_timestamp", current_timestamp()))
    out.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.gold, "ad_daily_yield"))
    logger.info("gold.ad_daily_yield built")

def build_discovery_daily(spark: SparkSession, c: CatalogConfig) -> None:
    search = spark.table(c.t(c.silver, "fact_search"))
    out = (search.groupBy(col("event_date").alias("kpi_date"), "query")
           .agg(
              count("*").alias("searches"),
              fsum(when(col("clicked_content_id").isNotNull(),1).otherwise(0)).alias("clickthroughs")
           )
           .withColumn("ctr", when(col("searches")>0, col("clickthroughs")/col("searches")).otherwise(lit(0.0)))
           .withColumn("ingestion_timestamp", current_timestamp()))
    out.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.gold, "discovery_daily"))
    logger.info("gold.discovery_daily built")

def build_qoe_daily_summary(spark: SparkSession, c: CatalogConfig) -> None:
    qoe = spark.table(c.t(c.silver, "fact_qoe"))
    geo = spark.table(c.t(c.silver, "dim_geo"))
    plat = spark.table(c.t(c.silver, "dim_platform"))
    dev = spark.table(c.t(c.silver, "dim_device"))

    # join keys from sessions by session_id (optional). Keep simple by using dim tables via existing event keys not present; so infer from user_events in future.
    # Here we publish a basic daily error count (still useful for dashboards).
    out = (qoe.groupBy(col("event_date").alias("kpi_date"))
           .agg(count("*").alias("error_events"))
           .withColumn("error_rate", lit(None).cast("double"))
           .withColumn("country", lit(None).cast("string"))
           .withColumn("region", lit(None).cast("string"))
           .withColumn("platform", lit(None).cast("string"))
           .withColumn("device_type", lit(None).cast("string"))
           .withColumn("ingestion_timestamp", current_timestamp())
           .select("kpi_date","country","region","platform","device_type","error_events","error_rate","ingestion_timestamp"))
    out.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.gold, "qoe_daily_summary"))
    logger.info("gold.qoe_daily_summary built")
