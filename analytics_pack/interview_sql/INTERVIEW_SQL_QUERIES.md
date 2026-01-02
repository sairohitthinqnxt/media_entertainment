# Interview SQL Queries (Analyst + Analytics Engineer)

Assume catalog `media_lakehouse` and Gold marts exist.

## 1) Top 10 content by engagement score for last 7 days
```sql
SELECT content_id, genre, content_type, SUM(engagement_score) AS score
FROM gold.vw_kpi_content_daily
WHERE kpi_date >= date_sub(current_date(), 7)
GROUP BY 1,2,3
ORDER BY score DESC
LIMIT 10;
```

## 2) DAU trend by platform (last 30 days)
```sql
SELECT kpi_date, platform, SUM(dau) AS dau
FROM gold.audience_daily_engagement
WHERE kpi_date >= date_sub(current_date(), 30)
GROUP BY 1,2
ORDER BY 1,2;
```

## 3) Search queries with worst zero-result rate (yesterday)
```sql
SELECT query, searches, clickthroughs, zero_result_rate
FROM gold.vw_kpi_discovery_daily
WHERE kpi_date = date_sub(current_date(), 1)
  AND searches >= 100
ORDER BY zero_result_rate DESC
LIMIT 50;
```

## 4) Ad yield: best placements by RPM (last 14 days)
```sql
SELECT placement, ad_format, SUM(revenue_usd) AS revenue, SUM(impressions) AS imps,
       (SUM(revenue_usd) * 1000) / NULLIF(SUM(impressions),0) AS rpm
FROM gold.ad_daily_yield
WHERE kpi_date >= date_sub(current_date(), 14)
GROUP BY 1,2
ORDER BY rpm DESC;
```

## 5) Completion rate by genre (last 7 days)
```sql
SELECT genre,
       SUM(completion_events) / NULLIF(SUM(views),0) AS completion_rate
FROM gold.content_daily_kpis
WHERE kpi_date >= date_sub(current_date(), 7)
GROUP BY genre
ORDER BY completion_rate DESC;
```

## 6) Returning user rate 7d (trend)
```sql
SELECT *
FROM gold.vw_kpi_returning_users_daily
WHERE kpi_date >= date_sub(current_date(), 30)
ORDER BY kpi_date;
```

## 7) Identify “power users” (top 1% watch time) last 30 days
```sql
WITH user_watch AS (
  SELECT user_id, SUM(total_watch_time_sec) AS wt
  FROM silver.fact_sessions
  WHERE session_date >= date_sub(current_date(), 30)
  GROUP BY user_id
),
p AS (
  SELECT percentile_approx(wt, 0.99) AS p99 FROM user_watch
)
SELECT u.user_id, u.wt
FROM user_watch u CROSS JOIN p
WHERE u.wt >= p.p99
ORDER BY u.wt DESC;
```

## 8) Funnel: Search → clickthrough → play (last 7 days)
```sql
WITH s AS (
  SELECT event_date AS d, COUNT(*) AS searches,
         SUM(CASE WHEN clicked_content_id IS NOT NULL THEN 1 ELSE 0 END) AS clickthroughs
  FROM silver.fact_search
  WHERE event_date >= date_sub(current_date(), 7)
  GROUP BY event_date
),
p AS (
  SELECT event_date AS d, COUNT(*) AS plays
  FROM silver.fact_playback
  WHERE event_date >= date_sub(current_date(), 7) AND event_type='play'
  GROUP BY event_date
)
SELECT s.d,
       s.searches,
       s.clickthroughs,
       p.plays,
       s.clickthroughs / NULLIF(s.searches,0) AS search_ctr,
       p.plays / NULLIF(s.clickthroughs,0) AS click_to_play_rate
FROM s LEFT JOIN p ON s.d = p.d
ORDER BY s.d;
```
