# Power BI Dashboard Layout (Spec)

## Page 1 — Executive Overview
**KPI cards (top row)**
- DAU (today vs yesterday)
- Watch Time (7d)
- Ad Revenue (7d)
- Active Subs (today)
- Churn Rate (today)
- Search CTR (yesterday)

**Charts**
1) Line: DAU (30d) by platform
2) Bar: Top 10 content by engagement score (7d)
3) Line: Ad revenue + RPM (14d)
4) Table: Worst zero-result queries (yesterday, searches>=100)
5) KPI: QoE error events (7d)

**Datasets / Tables**
- `gold.audience_daily_engagement` / `gold.vw_kpi_returning_users_daily`
- `gold.vw_kpi_content_daily`
- `gold.ad_daily_yield`
- `gold.vw_kpi_discovery_daily`
- `gold.qoe_daily_summary`

## Page 2 — Content Performance
- Slicers: date range, genre, content_type, language
- Matrix: content_id/title with views, unique viewers, completion rate, engagement score
- Trend: views & completion rate over time (selected content)

## Page 3 — Audience Engagement
- Slicers: country, platform, device_type
- Trend: DAU & sessions
- Scatter: avg_session_watch_time vs avg_events_per_session (by platform/device)

## Page 4 — Ads & Monetization
- Slicers: campaign_id, placement, ad_format
- Table: impressions/clicks/CTR/revenue/RPM
- Trend: RPM by placement

## Page 5 — Discovery & Search
- Table: top queries, CTR, zero-result rate
- Trend: searches & clickthroughs
- Bar: zero-result rate by query (top 20)

## Recommended Power BI Model
- Import Gold tables only (simple)
- Relationships:
  - content_id between content KPIs and dim_content (optional)
  - date table to kpi_date
