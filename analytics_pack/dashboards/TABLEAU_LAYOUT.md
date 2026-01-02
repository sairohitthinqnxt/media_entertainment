# Tableau Dashboard Layout (Spec)

## Workbook structure
**Dashboards**
1) Exec Overview
2) Content Performance
3) Audience Engagement
4) Ads Yield
5) Discovery & Search

## Example sheets (Exec Overview)
- DAU Trend (line)
- Engagement Score Top Content (bar)
- RPM Trend (line)
- Zero Result Queries (table)
- Country Heatmap (optional)

## Data sources
Connect to Databricks SQL warehouse and use:
- `media_lakehouse.gold.vw_kpi_content_daily`
- `media_lakehouse.gold.vw_kpi_audience_daily`
- `media_lakehouse.gold.vw_kpi_ad_daily`
- `media_lakehouse.gold.vw_kpi_discovery_daily`
