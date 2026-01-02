-- Run in Databricks SQL
-- Assumes catalog: media_lakehouse
USE CATALOG media_lakehouse;

-- Audience daily with bounce + sessions/user
CREATE OR REPLACE VIEW gold.vw_kpi_audience_daily AS
SELECT
  kpi_date,
  country, region, platform, device_type,
  dau,
  sessions,
  avg_session_watch_time_sec,
  avg_events_per_session,
  CASE WHEN dau > 0 THEN sessions / dau ELSE NULL END AS sessions_per_user,
  -- bounce: sessions where total_events <= 1
  SUM(CASE WHEN s.total_events <= 1 THEN 1 ELSE 0 END) AS bounce_sessions,
  CASE WHEN sessions > 0 THEN SUM(CASE WHEN s.total_events <= 1 THEN 1 ELSE 0 END) / sessions ELSE NULL END AS bounce_rate,
  MAX(ingestion_timestamp) AS ingestion_timestamp
FROM gold.audience_daily_engagement g
LEFT JOIN (
  SELECT session_date, geo_key, platform_key, device_key, total_events
  FROM silver.fact_sessions
) s
  ON s.session_date = g.kpi_date
GROUP BY 1,2,3,4,5,6,7,8,9;

-- Content daily with engagement score + dropoff proxy
CREATE OR REPLACE VIEW gold.vw_kpi_content_daily AS
SELECT
  kpi_date,
  content_id,
  genre,
  content_type,
  views,
  unique_viewers,
  watch_time_sec,
  avg_watch_time_sec,
  completion_events,
  completion_rate,
  likes,
  shares,
  ad_impressions,
  ad_clicks,
  ctr,
  ad_revenue_usd,
  sentiment_avg,
  -- engagement score (tunable)
  (views * 0.30) + (unique_viewers * 0.30) + (COALESCE(likes,0) * 0.20) + (COALESCE(shares,0) * 0.20) AS engagement_score,
  ingestion_timestamp
FROM gold.content_daily_kpis;

-- Discovery daily with zero-result rate
CREATE OR REPLACE VIEW gold.vw_kpi_discovery_daily AS
SELECT
  kpi_date,
  query,
  searches,
  clickthroughs,
  ctr,
  CASE WHEN searches > 0 THEN (searches - clickthroughs) / searches ELSE NULL END AS zero_result_rate,
  ingestion_timestamp
FROM gold.discovery_daily;

-- Ads daily yield view (adds effective CPC, eCPM proxies)
CREATE OR REPLACE VIEW gold.vw_kpi_ad_daily AS
SELECT
  kpi_date,
  campaign_id,
  placement,
  ad_format,
  impressions,
  clicks,
  ctr,
  revenue_usd,
  rpm,
  CASE WHEN clicks > 0 THEN revenue_usd / clicks ELSE NULL END AS revenue_per_click,
  ingestion_timestamp
FROM gold.ad_daily_yield;

-- Subscriptions daily with churn proxy
CREATE OR REPLACE VIEW gold.vw_kpi_subscription_daily AS
SELECT
  kpi_date,
  plan_name,
  active_subscriptions,
  new_subscriptions,
  cancellations,
  (new_subscriptions - cancellations) AS net_subscriber_change,
  CASE WHEN active_subscriptions > 0 THEN cancellations / active_subscriptions ELSE NULL END AS churn_rate,
  ingestion_timestamp
FROM gold.subscription_daily_summary;

-- Returning users (7d) - daily
-- Note: computes from sessions; can be materialized if needed
CREATE OR REPLACE VIEW gold.vw_kpi_returning_users_daily AS
WITH daily_users AS (
  SELECT session_date AS kpi_date, user_id
  FROM silver.fact_sessions
  GROUP BY 1,2
),
prev7 AS (
  SELECT a.kpi_date, a.user_id
  FROM daily_users a
  JOIN daily_users b
    ON a.user_id = b.user_id
   AND b.kpi_date BETWEEN date_sub(a.kpi_date, 7) AND date_sub(a.kpi_date, 1)
  GROUP BY a.kpi_date, a.user_id
)
SELECT
  d.kpi_date,
  COUNT(DISTINCT d.user_id) AS dau,
  COUNT(DISTINCT p.user_id) AS returning_users_7d,
  CASE WHEN COUNT(DISTINCT d.user_id) > 0 THEN COUNT(DISTINCT p.user_id) / COUNT(DISTINCT d.user_id) ELSE NULL END AS returning_user_rate_7d
FROM daily_users d
LEFT JOIN prev7 p
  ON d.kpi_date = p.kpi_date AND d.user_id = p.user_id
GROUP BY d.kpi_date;
