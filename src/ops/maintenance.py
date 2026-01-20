from pyspark.sql import SparkSession
from src.common.logging_utils import get_logger
logger = get_logger(__name__)

def optimize(spark: SparkSession, tables: list[str]) -> None:
    for t in tables:
        logger.info(f"OPTIMIZE {t}")
        spark.sql(f"OPTIMIZE {t}")

def vacuum(spark: SparkSession, tables: list[str], retain_hours: int=168) -> None:
    for t in tables:
        logger.info(f"VACUUM {t} RETAIN {retain_hours} HOURS")
        spark.sql(f"VACUUM {t} RETAIN {retain_hours} HOURS")
