import asyncio
import random

import pytest

from aredis_om import get_redis_connection


TEST_PREFIX = "redis-om:testing"


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def redis():
    yield get_redis_connection()


def _delete_test_keys(prefix: str, conn):
    keys = []
    for key in conn.scan_iter(f"{prefix}:*"):
        keys.append(key)
    if keys:
        conn.delete(*keys)


@pytest.fixture
def key_prefix(request, redis):
    key_prefix = f"{TEST_PREFIX}:{random.random()}"
    yield key_prefix


@pytest.fixture(scope="session", autouse=True)
def cleanup_keys(request):
    def cleanup_keys():
        # Always use the sync Redis connection with finalizer. Setting up an
        # async finalizer should work, but I'm not suer how yet!
        from redis_om.connections import get_redis_connection as get_sync_redis
        _delete_test_keys(TEST_PREFIX, get_sync_redis())

    request.addfinalizer(cleanup_keys)
