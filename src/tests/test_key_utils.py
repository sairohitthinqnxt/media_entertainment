from src.common import key_utils
def test_key_utils_exports():
    assert callable(key_utils.device_key)
    assert callable(key_utils.geo_key)
    assert callable(key_utils.platform_key)
