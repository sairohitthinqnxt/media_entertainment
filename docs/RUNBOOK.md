# Runbook (Intermediate)

## Normal schedule
- Streaming: continuous user_events ingestion
- Hourly: build Silver facts (incremental window) + refresh Gold for last 2–3 days
- Daily: batch ingestions (content/users/subscriptions/campaigns/payments/social) + full Gold refresh if needed

## Late events strategy
Gold marts recompute a rolling window (default 3 days) to catch late arrivals.

## Common failures
- Schema drift in user_events: update schema + replay from Bronze for impacted dates
- Streaming backlog: tune maxFilesPerTrigger, scale cluster, check checkpoint health
- DQ spike: inspect quarantine_events by reason, validate upstream producer

## Backfill
1) Identify date range
2) Rebuild Silver facts for that range from Bronze
3) Rebuild Gold marts for that range
4) Reconcile key totals (plays, revenue, DAU)
