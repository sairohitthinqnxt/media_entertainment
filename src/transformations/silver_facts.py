from __future__ import annotations
from pyspark.sql import SparkSession
from pyspark.sql.functions import col,lower, to_date, current_timestamp, lit, min as fmin, max as fmax, sum as fsum, count as fcount, when
from src.common.config import CatalogConfig
from src.common.logging_utils import get_logger
from src.common.key_utils import device_key, geo_key, platform_key
from src.dq.rules import RULES_USER_EVENTS
from src.dq.runner import run_dq

logger = get_logger(__name__)

def _enrich_keys(df):
    return (df
        .withColumn("device_key", device_key())
        .withColumn("geo_key", geo_key())
        .withColumn("platform_key", platform_key())
    )

def build_fact_playback(spark: SparkSession, c: CatalogConfig) -> None:
    raw = spark.table(c.t(c.bronze, "user_events_raw"))
   
    passed, failed = run_dq(spark, raw, RULES_USER_EVENTS, "bronze", "user_events_raw", c)
   

    if failed.count() > 0:
        failed.select(current_timestamp().alias("ingestion_timestamp"),
                      lit("user_events_raw").alias("source"),
                      lit("dq_failed").alias("reason"),
                      col("raw_payload").cast("string").alias("raw_payload")).write.format("delta").mode("append").saveAsTable(c.t(c.bronze, "quarantine_events"))

    ev = _enrich_keys(passed).withColumn("event_date", to_date(col("event_ts")))
    ev = ev.dropDuplicates(["event_id"]) if "event_id" in ev.columns else ev.dropDuplicates(["user_id","session_id","event_ts","event_type","content_id"])

    playback = ev.filter(col("event_type").isin("PLAY", "PAUSE", "STOP", "SEARCH","COMPLETE","SEARCH"))
    playback.select(
        "event_id","user_id","session_id","content_id","event_type","event_ts","event_date",
        "position_sec","watch_time_sec","device_key","geo_key","platform_key","ingestion_timestamp"
    ).write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver, "fact_playback"))
    logger.info("fact_playback built")

def build_fact_search(spark: SparkSession, c: CatalogConfig) -> None:
    ev = spark.table(c.t(c.bronze, "user_events_raw"))
    ev = _enrich_keys(ev).withColumn("event_date", to_date(col("event_ts"))).dropDuplicates(["event_id"])
    search = ev.filter(col("event_type") == "SEARCH")
    search.select(
        "event_id","user_id","session_id","event_ts","event_date","query","clicked_content_id",
        "device_key","geo_key","platform_key","ingestion_timestamp"
    ).write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver, "fact_search"))
    logger.info("fact_search built")

def build_fact_sessions(spark: SparkSession, c: CatalogConfig) -> None:
    ev = spark.table(c.t(c.silver, "fact_playback"))
    sess = (ev.groupBy("session_id","user_id","device_key","geo_key","platform_key")
            .agg(
                fmin("event_ts").alias("session_start_ts"),
                fmax("event_ts").alias("session_end_ts"),
                fsum(when(col("watch_time_sec").isNull(),0).otherwise(col("watch_time_sec"))).alias("total_watch_time_sec"),
                fcount(lit(1)).alias("total_events"),
                fmax("ingestion_timestamp").alias("ingestion_timestamp"),
            )
            .withColumn("session_date", to_date(col("session_start_ts")))
            .withColumn("referrer", lit(None).cast("string")))
    sess.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver, "fact_sessions"))
    logger.info("fact_sessions built")

def build_fact_ad_events(spark: SparkSession, c: CatalogConfig) -> None:
    ads = spark.table(c.t(c.bronze, "ad_events_raw")).filter(col("event_ts").isNotNull())
    df = ads.withColumn("event_date", to_date(col("event_ts"))).dropDuplicates(["ad_event_id"])
    df.select(
        "ad_event_id","user_id","session_id","content_id","ad_id","campaign_id","placement","ad_format",
        "event_type","event_ts","event_date","revenue_usd","ingestion_timestamp"
    ).write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver, "fact_ad_events"))
    logger.info("fact_ad_events built")

def build_fact_payments(spark: SparkSession, c: CatalogConfig) -> None:
    pay = spark.table(c.t(c.bronze, "payment_raw")).filter(col("payment_ts").isNotNull())
    df = pay.withColumn("payment_date", to_date(col("payment_ts"))).dropDuplicates(["payment_id"])
    df.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver, "fact_payments"))
    logger.info("fact_payments built")

def build_fact_social_signals(spark: SparkSession, c: CatalogConfig) -> None:
    ss = spark.table(c.t(c.bronze, "social_signals_raw")).filter(col("mention_ts").isNotNull())
    df = ss.withColumn("mention_date", to_date(col("mention_ts"))).dropDuplicates(["signal_id"])
    df.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver, "fact_social_signals"))
    logger.info("fact_social_signals built")

def build_fact_qoe(spark: SparkSession, c: CatalogConfig) -> None:
    # lightweight QoE based on error_code in user events
    ev = spark.table(c.t(c.bronze, "user_events_raw")).filter(col("event_ts").isNotNull())
    df = (ev.filter(col("error_code").isNotNull())
          .select(col("event_id").alias("qoe_event_id"), "user_id","session_id","content_id","event_ts", to_date(col("event_ts")).alias("event_date"), "error_code", "ingestion_timestamp")
          .dropDuplicates(["qoe_event_id"]))
    df.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver, "fact_qoe"))
    logger.info("fact_qoe built")
