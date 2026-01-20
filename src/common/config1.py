#Catalog Config
from dataclasses import dataclass

@dataclass(frozen=True)
class CatalogConfig:
    catalog: str = "media_lakehouse"
    bronze: str = "bronze"
    silver: str = "silver"
    gold: str = "gold"
    def t(self, schema: str, table: str) -> str:
        return f"{self.catalog}.{schema}.{table}"



