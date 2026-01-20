CREATE CATALOG IF NOT EXISTS media_lakehouse;
"""CREATE SCHEMA IF NOT EXISTS media_lakehouse.bronze;
CREATE SCHEMA IF NOT EXISTS media_lakehouse.silver;
CREATE SCHEMA IF NOT EXISTS media_lakehouse.gold;

-- ========== BRONZE ==========
CREATE TABLE IF NOT EXISTS media_lakehouse.bronze.content_raw (
  content_id STRING, title STRING, content_type STRING, genre STRING, language STRING,
  release_date DATE, duration_sec INT, publisher STRING, tags ARRAY<STRING>, last_updated TIMESTAMP,
  ingestion_timestamp TIMESTAMP, source_file STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.bronze.user_profile_raw (
  user_id STRING, signup_ts TIMESTAMP, country STRING, region STRING, language STRING,
  age_band STRING, marketing_opt_in BOOLEAN, last_updated TIMESTAMP,
  ingestion_timestamp TIMESTAMP, source_file STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.bronze.subscription_raw (
  subscription_id STRING, user_id STRING, plan_name STRING, price_usd DECIMAL(18,2),
  status STRING, start_date DATE, end_date DATE, cancel_reason STRING, last_updated TIMESTAMP,
  ingestion_timestamp TIMESTAMP, source_file STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.bronze.campaign_raw (
  campaign_id STRING, advertiser STRING, campaign_name STRING, objective STRING,
  start_date DATE, end_date DATE, last_updated TIMESTAMP,
  ingestion_timestamp TIMESTAMP, source_file STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.bronze.payment_raw (
  payment_id STRING, subscription_id STRING, user_id STRING, payment_ts TIMESTAMP,
  amount_usd DECIMAL(18,2), status STRING, provider STRING,
  ingestion_timestamp TIMESTAMP, source_file STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.bronze.ad_events_raw (
  ad_event_id STRING, user_id STRING, session_id STRING, content_id STRING,
  ad_id STRING, campaign_id STRING, placement STRING, ad_format STRING,
  event_type STRING, event_ts TIMESTAMP, revenue_usd DECIMAL(18,6),
  ingestion_timestamp TIMESTAMP, raw_payload STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.bronze.social_signals_raw (
  signal_id STRING, platform STRING, content_id STRING, mention_ts TIMESTAMP,
  sentiment DOUBLE, mentions INT, engagement INT,
  ingestion_timestamp TIMESTAMP, raw_payload STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.bronze.user_events_raw (
  event_id STRING, user_id STRING, session_id STRING, content_id STRING,
  event_type STRING, event_ts TIMESTAMP, position_sec INT, watch_time_sec INT,
  query STRING, clicked_content_id STRING,
  device_type STRING, os STRING, app_version STRING, platform STRING,
  country STRING, region STRING, referrer STRING,
  error_code STRING,
  ingestion_timestamp TIMESTAMP, raw_payload STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.bronze.quarantine_events (
  ingestion_timestamp TIMESTAMP, source STRING, reason STRING, raw_payload STRING
) USING DELTA;

-- ========== SILVER DIMENSIONS (SCD1-ish) ==========
CREATE TABLE IF NOT EXISTS media_lakehouse.silver.dim_content USING DELTA AS SELECT * FROM media_lakehouse.bronze.content_raw WHERE 1=0;
CREATE TABLE IF NOT EXISTS media_lakehouse.silver.dim_user    USING DELTA AS SELECT * FROM media_lakehouse.bronze.user_profile_raw WHERE 1=0;
CREATE TABLE IF NOT EXISTS media_lakehouse.silver.dim_subscription USING DELTA AS SELECT * FROM media_lakehouse.bronze.subscription_raw WHERE 1=0;
CREATE TABLE IF NOT EXISTS media_lakehouse.silver.dim_campaign USING DELTA AS SELECT * FROM media_lakehouse.bronze.campaign_raw WHERE 1=0;

CREATE TABLE IF NOT EXISTS media_lakehouse.silver.dim_device (
  device_key STRING, device_type STRING, os STRING, app_version STRING, ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.silver.dim_geo (
  geo_key STRING, country STRING, region STRING, ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.silver.dim_platform (
  platform_key STRING, platform STRING, ingestion_timestamp TIMESTAMP
) USING DELTA;

-- ========== SILVER FACTS ==========
CREATE TABLE IF NOT EXISTS media_lakehouse.silver.fact_playback (
  event_id STRING, user_id STRING, session_id STRING, content_id STRING, event_type STRING,
  event_ts TIMESTAMP, event_date DATE, position_sec INT, watch_time_sec INT,
  device_key STRING, geo_key STRING, platform_key STRING, ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.silver.fact_search (
  event_id STRING, user_id STRING, session_id STRING, event_ts TIMESTAMP, event_date DATE,
  query STRING, clicked_content_id STRING,
  device_key STRING, geo_key STRING, platform_key STRING, ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.silver.fact_sessions (
  session_id STRING, user_id STRING, session_start_ts TIMESTAMP, session_end_ts TIMESTAMP,
  session_date DATE, device_key STRING, geo_key STRING, platform_key STRING,
  referrer STRING, total_watch_time_sec BIGINT, total_events BIGINT, ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.silver.fact_ad_events (
  ad_event_id STRING, user_id STRING, session_id STRING, content_id STRING, ad_id STRING, campaign_id STRING,
  placement STRING, ad_format STRING, event_type STRING, event_ts TIMESTAMP, event_date DATE,
  revenue_usd DECIMAL(18,6), ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.silver.fact_payments (
  payment_id STRING, subscription_id STRING, user_id STRING, payment_ts TIMESTAMP, payment_date DATE,
  amount_usd DECIMAL(18,2), status STRING, provider STRING, ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.silver.fact_social_signals (
  signal_id STRING, platform STRING, content_id STRING, mention_ts TIMESTAMP, mention_date DATE,
  sentiment DOUBLE, mentions INT, engagement INT, ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.silver.fact_qoe (
  qoe_event_id STRING, user_id STRING, session_id STRING, content_id STRING,
  event_ts TIMESTAMP, event_date DATE, error_code STRING,
  ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.silver.dq_metrics (
  run_id STRING, run_ts TIMESTAMP, layer STRING, table_name STRING,
  rule_name STRING, passed BIGINT, failed BIGINT, notes STRING
) USING DELTA;

-- ========== GOLD MARTS ==========
CREATE TABLE IF NOT EXISTS media_lakehouse.gold.content_daily_kpis (
  kpi_date DATE, content_id STRING, genre STRING, content_type STRING,
  views BIGINT, unique_viewers BIGINT, watch_time_sec BIGINT, avg_watch_time_sec DOUBLE,
  completion_events BIGINT, completion_rate DOUBLE,
  likes BIGINT, shares BIGINT,
  ad_impressions BIGINT, ad_clicks BIGINT, ctr DOUBLE, ad_revenue_usd DECIMAL(18,6),
  sentiment_avg DOUBLE, ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.gold.audience_daily_engagement (
  kpi_date DATE, country STRING, region STRING, platform STRING, device_type STRING,
  dau BIGINT, sessions BIGINT, avg_session_watch_time_sec DOUBLE, avg_events_per_session DOUBLE,
  ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.gold.subscription_daily_summary (
  kpi_date DATE, plan_name STRING,
  active_subscriptions BIGINT, new_subscriptions BIGINT, cancellations BIGINT,
  ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.gold.ad_daily_yield (
  kpi_date DATE, campaign_id STRING, placement STRING, ad_format STRING,
  impressions BIGINT, clicks BIGINT, ctr DOUBLE, revenue_usd DECIMAL(18,6), rpm DOUBLE,
  ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.gold.discovery_daily (
  kpi_date DATE, query STRING,
  searches BIGINT, clickthroughs BIGINT, ctr DOUBLE,
  ingestion_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS media_lakehouse.gold.qoe_daily_summary (
  kpi_date DATE, country STRING, region STRING, platform STRING, device_type STRING,
  error_events BIGINT, error_rate DOUBLE,
  ingestion_timestamp TIMESTAMP
) USING DELTA;"""
