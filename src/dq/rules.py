from dataclasses import dataclass

@dataclass(frozen=True)
class DQRule:
    name: str
    description: str
    predicate_sql: str  # rows that pass

# Intermediate but still simple
RULES_USER_EVENTS = [
    DQRule("not_null_user", "user_id must exist", "user_id IS NOT NULL"),
    DQRule("not_null_event_ts", "event_ts must exist", "event_ts IS NOT NULL"),
    DQRule("valid_event_type", "event_type must be known", "event_type IN ('SESSION_START','SESSION_END','PLAY','PAUSE','STOP','COMPLETE','SEARCH','LIKE','SHARE','CLICK')"),
    DQRule("watch_time_non_negative", "watch_time_sec must be >=0", "watch_time_sec IS NULL OR watch_time_sec >= 0"),
]