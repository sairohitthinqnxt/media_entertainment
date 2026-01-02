# Upgrade to Analytics Engineer Level (No heavy SCD2)

This repo is already close to AE responsibilities. To make it AE-level, implement:

## 1) Metric layer + semantic consistency
- Keep KPI definitions in a versioned dictionary (already added).
- Standardize naming: `kpi_date`, `ingestion_timestamp`.
- Decide and document “view” threshold: e.g., play with watch_time_sec >= 10 sec.

## 2) Incremental model patterns
- Convert Gold builds to incremental refresh with date partitions:
  - recompute last 3 days (late arrivals)
  - merge into gold tables on (kpi_date, grain keys)

## 3) Add a Date Dimension + conformed dimensions
- `dim_date`: fiscal weeks, quarters, holidays
- `dim_content` and `dim_campaign` should be used in BI model relationships

## 4) Data testing culture
- Add tests for:
  - non-null keys
  - accepted values for event_type
  - uniqueness on ids
  - freshness (latest partition exists)
- Use `dq_metrics` as an observable table

## 5) Observability
- Pipeline metrics: row counts per table per run, lag for streaming, quarantine rate.
- Alerts: DQ failure spike, no data today, sudden drop in DAU.

## 6) dbt mapping (optional)
If org uses dbt, map:
- Bronze tables: sources
- Silver dims/facts: staging models
- Gold marts: intermediate + mart models
Metric views become `metrics` or `semantic models`.

## 7) BI readiness
- Publish `gold.vw_kpi_*` views as the only BI-facing layer.
- Restrict access to raw/bronze schemas for data governance.
