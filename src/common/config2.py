#Catalog Config
from dataclasses import dataclass


#storage config  
@dataclass(frozen=True)
class StorageConfig:
    landing_base="abfss://source@babustorage01.dfs.core.windows.net/"
    schema_location="abfss://forcat@babustorage01.dfs.core.windows.net/"
    checkpoint_location="abfss://forcat@babustorage01.dfs.core.windows.net/"