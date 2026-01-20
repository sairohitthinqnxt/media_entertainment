from pyspark.sql.functions import sha2, concat_ws, col

def device_key():
    return sha2(concat_ws("||", col("device_type"), col("os"), col("app_version")), 256)

def geo_key():
    return sha2(concat_ws("||", col("country"), col("region")), 256)

def platform_key():
    return sha2(col("platform").cast("string"), 256)
