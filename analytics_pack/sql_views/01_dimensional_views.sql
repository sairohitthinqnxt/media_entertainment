USE CATALOG media_lakehouse;

-- Helpful analyst views with joined dimensions (no heavy semantic layer)
CREATE OR REPLACE VIEW silver.vw_playback_enriched AS
SELECT
  p.*,
  dc.title, dc.genre, dc.content_type, dc.language,
  du.country AS user_country, du.region AS user_region, du.language AS user_language
FROM silver.fact_playback p
LEFT JOIN silver.dim_content dc ON p.content_id = dc.content_id
LEFT JOIN silver.dim_user du ON p.user_id = du.user_id;

CREATE OR REPLACE VIEW silver.vw_sessions_enriched AS
SELECT
  s.*,
  g.country, g.region,
  d.device_type, d.os, d.app_version,
  pl.platform
FROM silver.fact_sessions s
LEFT JOIN silver.dim_geo g ON s.geo_key = g.geo_key
LEFT JOIN silver.dim_device d ON s.device_key = d.device_key
LEFT JOIN silver.dim_platform pl ON s.platform_key = pl.platform_key;
