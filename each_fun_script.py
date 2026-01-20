from pyspark.sql.functions import date_format,current_timestamp,col,current_date
def count_incoming_data(spark,tables_list,layer):
    for i in tables_list:
        table=spark.table(f"media_lakehouse.{layer}.{i}")
        df=table.filter(date_format(col("ingestion_timestamp"),"yyyy-MM-dd")==date_format(current_timestamp(),"yyyy-MM-dd"))
        table_name=i
        no_of_records=df.count()
        spark.createDataFrame([(table_name,no_of_records)],["table_name","no_of_records"])\
            .withColumn("up_to_date",current_date())\
                .withColumn("no_of_records",col("no_of_records").cast("int"))\
                .write.mode("append").option("mergeSchema", "true").saveAsTable(f"media_lakehouse.{layer}.data_details")
        


        