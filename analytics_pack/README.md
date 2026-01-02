# Analytics Pack (Added)

This folder adds analyst/BI assets to the 3-YOE repo.

## Contents
- `sql_views/` : Databricks SQL views for KPIs (audience, content, discovery, ads, subscriptions, returning users)
- `dashboards/` : Power BI and Tableau dashboard layout specs + a Tableau skeleton workbook
- `KPI_DICTIONARY.md` : metric definitions
- `interview_sql/` : common interview SQL questions
- `ae_upgrade/` : how to present/upgrade this project as an Analytics Engineer

## Quick start
1) Run base pipeline to build Silver/Gold tables.
2) Execute: `sql_views/00_create_views.sql`
3) Connect Power BI / Tableau to the `gold.vw_kpi_*` views.
