from __future__ import annotations
import uuid
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import current_timestamp
from src.dq.rules import DQRule
from src.common.config import CatalogConfig
from src.common.logging_utils import get_logger

def run_dq(
    spark: SparkSession,
    df: DataFrame,
    rules: list[DQRule],
    layer: str,
    table_name: str,
    catalog_config: CatalogConfig
) -> tuple[DataFrame, DataFrame]:

    run_id = str(uuid.uuid4())
    metrics_table = catalog_config.t(catalog_config.silver, "metrics")

    failed_all = None

    for r in rules:
        passed = df.filter(r.predicate_sql)
        failed = df.filter(f"NOT ({r.predicate_sql})")

        passed_cnt = passed.count()
        failed_cnt = failed.count()

        metrics = spark.createDataFrame(
            [(run_id, None, layer, table_name, r.name, passed_cnt, failed_cnt, r.description)],
            "run_id string, run_ts timestamp, layer string, table_name string, rule_name string, passed long, failed long, notes string"
        ).withColumn("run_ts", current_timestamp())

        metrics.write.format("delta").mode("append").saveAsTable(metrics_table)

        failed_all = failed if failed_all is None else failed_all.unionByName(
            failed, allowMissingColumns=True
        )

    # Rows that failed ANY rule
    if failed_all is None:
        failed_all = df.limit(0)

    # Rows that passed ALL rules
    passed_all = df.subtract(failed_all)

    return passed_all, failed_all




