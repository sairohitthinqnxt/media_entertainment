# media_entertainment_lakehouse_3yoe

**3-years-experience (Intermediate) scope** Media & Entertainment Lakehouse.

✅ Many tables, lots of realistic transformations, real pipeline structure  
❌ No heavy SCD2 frameworks / slowly changing merges (keeps it interview-ready for ~3 YOE)  
❌ No overly advanced “enterprise mega marts” (keep marts focused and readable)

## What you get
- Medallion: **Bronze → Silver → Gold** (Delta)
- Batch ingestion: CMS content, user profiles, subscriptions, campaigns, payments, social signals
- Streaming ingestion: user events (Auto Loader JSON)
- Silver transformations:
  - Schema enforcement & casting
  - Deduping (event_id and compound keys)
  - Standardized dimensions (content/user/device/geo/platform/campaign/subscription)
  - Facts: sessions, playback, search, ads, payments, social, QoE (lightweight)
  - Late-data window support for Gold recalculation
- Gold marts (intermediate):
  - content_daily_kpis
  - audience_daily_engagement
  - subscription_daily_summary
  - ad_daily_yield
  - discovery_daily (search + clickthrough)
  - qoe_daily_summary
- Data quality:
  - rules + quarantine + DQ metrics table
- Orchestration:
  - Databricks Workflows YAML (simple dependency graph)
  - Optional Airflow skeleton
- Tests: unit-style checks for key transforms utilities

## Start here
1) Create tables: `docs/DDL.sql`
2) Read: `docs/PROJECT_GUIDE.md`
3) Run notebooks: `notebooks/01_ingest_bronze.py` → `02_build_silver.py` → `03_build_gold.py`


## Analyst assets
See `analytics_pack/` for KPI views, dashboard layouts, KPI dictionary, and interview SQL.
