from pyspark.sql import SparkSession,DataFrame
from pyspark.sql.functions import * 
from pyspark.sql.types import *




#batch ingesting the data 
def ingest(spark:SparkSession, src_path:str, fmt : str,schema, target_table: str) -> None:
    reader=spark.read.format(fmt).schema(schema)
    df=(reader.load(src_path)
               . withColumn("ingestion_timestamp",current_timestamp())
               .withColumn("source_file",input_file_name()))

    df.write.mode("append").format("delta").option("mergeSchema",True).saveAsTable(target_table)


#for add events data
def ingest_rawpay(spark:SparkSession, src_path:str, fmt : str,schema, target_table: str) -> None:
    reader=spark.read.format(fmt).schema(schema)
    df=(reader.load(src_path)
               . withColumn("ingestion_timestamp",current_timestamp())
               .withColumn("raw_payload",input_file_name()))
    
    
    df.write.mode("append").format("delta").option("mergeSchema",True).saveAsTable(target_table)
    
   