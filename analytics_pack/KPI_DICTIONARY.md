# KPI Dictionary — Media & Entertainment (Analyst-Ready)

This document standardizes metric definitions so BI and analysts compute KPIs consistently.

## Global conventions
- Timezone: **UTC** (recommended). If business uses local time, define it explicitly and apply consistently.
- Grain:
  - Daily KPI tables use `kpi_date` (DATE).
  - Fact tables use event timestamps and derived `event_date`.
- Deduping:
  - `fact_playback` de-duplicates by `event_id` (or a compound key when missing).
  - `fact_ad_events` de-duplicates by `ad_event_id`.
- “View” definition:
  - Count of `event_type='play'` from `silver.fact_playback`.

---

## Audience Engagement KPIs (Gold / Views)
### DAU
**Definition:** Distinct active users with ≥1 session on `kpi_date`.  
**Formula:** `COUNT(DISTINCT user_id)` from `silver.fact_sessions` grouped by `session_date`.  
**Table/Field:** `gold.audience_daily_engagement.dau`

### Sessions
**Definition:** Distinct sessions on `kpi_date`.  
**Formula:** `COUNT(DISTINCT session_id)` from `silver.fact_sessions`.
**Table/Field:** `gold.audience_daily_engagement.sessions`

### Sessions per User
**Definition:** Avg sessions per active user.  
**Formula:** `sessions / dau`  
**Field:** `vw_kpi_audience_daily.sessions_per_user` (view)

### Avg Session Watch Time (sec)
**Definition:** Average watch time per session.  
**Formula:** `AVG(total_watch_time_sec)` from `silver.fact_sessions`  
**Table/Field:** `gold.audience_daily_engagement.avg_session_watch_time_sec`

### Bounce Sessions / Bounce Rate
**Definition:** A “bounce” is a session with very low engagement (default: `total_events <= 1`).  
**Bounce sessions:** count of sessions satisfying bounce rule.  
**Bounce rate:** `bounce_sessions / sessions`  
**Field:** `vw_kpi_audience_daily.bounce_rate` (view)

### Returning Users / Returning User Rate (7d)
**Definition:** Users active today that were active in the previous 7 days (excluding today).  
**Formula idea:** users where exists session in `[kpi_date-7, kpi_date-1]`.  
**Field:** `vw_kpi_returning_users_daily.returning_user_rate_7d`

---

## Content Performance KPIs
### Views
**Definition:** Total plays.  
**Formula:** `COUNT(*)` where `event_type='play'` from `silver.fact_playback`  
**Table/Field:** `gold.content_daily_kpis.views`

### Unique Viewers
**Definition:** Distinct users who played content.  
**Formula:** `COUNT(DISTINCT user_id)` where `event_type='play'`  
**Table/Field:** `gold.content_daily_kpis.unique_viewers`

### Watch Time (sec)
**Definition:** Total watch time summed across events.  
**Formula:** `SUM(watch_time_sec)` (treat null as 0) from playback.  
**Table/Field:** `gold.content_daily_kpis.watch_time_sec`

### Completion Rate
**Definition:** Completes / Plays.  
**Formula:** `completion_events / views`  
**Table/Field:** `gold.content_daily_kpis.completion_rate` (view version also available)

### Engagement Score (Analyst-friendly)
**Purpose:** Single number to rank content.  
**Default weights (tunable):**
- views 0.30
- unique_viewers 0.30
- likes 0.20
- shares 0.20
**Field:** `vw_kpi_content_daily.engagement_score`

---

## Discovery/Search KPIs
### Searches
**Definition:** Total search events.  
**Formula:** `COUNT(*)` from `silver.fact_search` grouped by date/query  
**Table/Field:** `gold.discovery_daily.searches`

### Search CTR
**Definition:** Clickthroughs / Searches.  
**Field:** `gold.discovery_daily.ctr`

### Zero-result rate
**Definition:** `(searches - clickthroughs) / searches`  
**Field:** `vw_kpi_discovery_daily.zero_result_rate`

---

## Ads & Monetization KPIs
### Impressions/Clicks/CTR
**Definition:** From `silver.fact_ad_events` (event types `impression`, `click`).  
**Gold:** `gold.ad_daily_yield`

### Revenue (USD)
**Definition:** Sum of `revenue_usd`.  
**Gold:** `gold.ad_daily_yield.revenue_usd`

### RPM
**Definition:** Revenue per 1000 impressions.  
**Formula:** `(revenue_usd * 1000) / impressions`  
**Gold:** `gold.ad_daily_yield.rpm`

---

## Subscriptions KPIs
### Active subscriptions
**Definition:** Count of subscriptions in active status (snapshot).  
**Gold:** `gold.subscription_daily_summary.active_subscriptions`

### Churn rate (daily proxy)
**Definition:** `cancellations / active_subscriptions` (proxy; true churn needs cohorting).  
**Field:** `vw_kpi_subscription_daily.churn_rate`

---

## QoE KPIs
### Error events
**Definition:** Count of events with `error_code` present.  
**Gold:** `gold.qoe_daily_summary.error_events`

---

## Notes for production
- Validate event-type taxonomy with product analytics team.
- Define “view” threshold (e.g., play with watch_time_sec >= 10s) if needed.
- Retention cohorts can be added later (AE upgrade document included).
