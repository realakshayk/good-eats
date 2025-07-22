import pytest
import os
from utils.cache import get_or_set_cache, invalidate_cache
import time

def test_cache_set_and_get(tmp_path, monkeypatch):
    key = 'test_key'
    value = {'foo': 'bar'}
    # Use a fetch_fn that returns value
    result = get_or_set_cache(key, 2, lambda: value)
    assert result == value
    # Should get from cache (no fetch)
    result2 = get_or_set_cache(key, 2, lambda: {'foo': 'baz'})
    assert result2 == value
    # Invalidate and ensure fetch_fn is called again
    invalidate_cache(key)
    result3 = get_or_set_cache(key, 2, lambda: {'foo': 'baz'})
    assert result3 == {'foo': 'baz'}


def test_file_cache_expiry(tmp_path, monkeypatch):
    key = 'test_expiry'
    value = {'bar': 'baz'}
    # Set with short TTL
    result = get_or_set_cache(key, 1, lambda: value)
    assert result == value
    time.sleep(1.1)
    # Should call fetch_fn again after expiry
    result2 = get_or_set_cache(key, 1, lambda: {'bar': 'new'})
    assert result2 == {'bar': 'new'} 