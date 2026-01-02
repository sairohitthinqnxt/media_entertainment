# Project Guide (3 YOE) — Intermediate Lakehouse

## Business problem
A media platform has data scattered across CMS, subscription/billing, ad systems, and client-event streams.
Teams want a single source of truth for:
- content performance (views, watch time, completion, shares/likes)
- audience engagement (DAU, sessions, session depth)
- monetization (ad yield, CTR, revenue by placement/campaign)
- discovery (search queries → clickthrough to content)
- QoE health (errors, buffering proxies)

## Data flow
Sources → Bronze (raw, replayable) → Silver (clean dims/facts) → Gold (daily marts)

## Scope choices (why)
- **No heavy SCD2**: 3-YOE scope focuses on stable, incremental pipelines + good modeling.
- **Gold marts are “dashboard-ready” but limited**: daily aggregates, not huge semantic layers.
- **DQ is practical**: required fields, type checks, and quarantine.

## Tables (overview)
### Bronze
- content_raw
- user_profile_raw
- subscription_raw
- campaign_raw
- payment_raw
- ad_events_raw
- social_signals_raw
- user_events_raw (stream)
- quarantine_events

### Silver dimensions (SCD1-ish overwrite or incremental merge)
- dim_content
- dim_user
- dim_subscription
- dim_campaign
- dim_device
- dim_geo
- dim_platform

### Silver facts
- fact_playback
- fact_sessions
- fact_search
- fact_ad_events
- fact_payments
- fact_social_signals
- fact_qoe (lightweight)

### Gold marts (intermediate)
- content_daily_kpis
- audience_daily_engagement
- subscription_daily_summary
- ad_daily_yield
- discovery_daily
- qoe_daily_summary

## Interview-ready summary
“I built a Delta Lakehouse with raw ingestion from batch exports and streaming events, standardized everything into conformed
dimensions and facts, and published daily KPI marts for content, engagement, subscriptions, ads, discovery, and QoE.
I also implemented basic DQ rules with quarantine and built a simple workflow orchestration.”
