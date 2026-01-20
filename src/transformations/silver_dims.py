from __future__ import annotations
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, sha2, concat_ws
from src.common.config import CatalogConfig
from src.common.logging_utils import get_logger
from src.common.key_utils import device_key, geo_key, platform_key

def build_dim_content(spark:sparkSession, c:catalogConfig) -> None:
    df=spark.table(c.t(c.bronze,"content_raw")).dropDuplicates(["content_id"])
    df.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver,"dim_content"))

def build_dim_user(spark:sparkSession, c:catalogConfig) -> None:
    df=spark.table(c.t(c.bronze,"user_profile_raw")).dropDuplicates(["user_id"])
    df.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver,"dim_user"))

def build_dim_subscription(spark:sparkSession, c:catalogConfig) -> None:
    df=spark.table(c.t(c.bronze,"subscription_raw")).dropDuplicates(["subscription_id"])
    df.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver,"dim_subscription"))

def build_dim_campaign(spark:sparkSession, c:catalogConfig) -> None:
    df=spark.table(c.t(c.bronze,"campaign_raw")).dropDuplicates(["campaign_id"])
    df.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver,"dim_campaign"))

def build_dim_device_geo_platform(spark:sparkSession, c:catalogConfig) -> None:
    ev=spark.table(c.t(c.bronze,"user_events_raw"))
    d=(ev.select("device_type","os","app_version").dropDuplicates()
       .withColumn("device_key",device_key())
        .withColumn("ingestion_timestamp",current_timestamp())
      )
    
    g=(ev.select("country","region").dropDuplicates()
       .withColumn("geo_key",geo_key())
       .withColumn("ingestion_timestamp",current_timestamp())
      )
    
    p=(ev.select("platform").dropDuplicates()
       .withColumn("platform_key",platform_key())
       .withColumn("ingestion_timestamp",current_timestamp()))
    

    d.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver,"dim_device"))
    g.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver,"dim_geo"))
    p.write.format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable(c.t(c.silver,"dim_platform"))
