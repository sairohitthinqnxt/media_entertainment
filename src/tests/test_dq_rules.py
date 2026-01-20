from src.dq.rules import RULES_USER_EVENTS
def test_dq_rules_non_empty():
    assert len(RULES_USER_EVENTS) >= 3
