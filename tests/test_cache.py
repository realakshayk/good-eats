import pytest
import tempfile
import os
import json

@pytest.fixture
def temp_cache_file():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(b'{"cached": true}')
        tf.flush()
        yield tf.name
    os.remove(tf.name)

def test_file_cache(temp_cache_file):
    with open(temp_cache_file, 'r') as f:
        data = json.load(f)
    assert data["cached"] is True 