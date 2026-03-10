import unittest
from unittest.mock import patch, sentinel

from flask import Flask

from app.core.redis_ext import get_redis, init_redis


class RedisExtTestCase(unittest.TestCase):
    def test_init_redis_uses_configured_url(self):
        app = Flask(__name__)
        app.config["REDIS_URL"] = "redis://example"

        with patch("app.core.redis_ext.redis.Redis.from_url", return_value=sentinel.client) as from_url:
            init_redis(app)

        from_url.assert_called_once_with("redis://example", decode_responses=True)
        self.assertIs(app.extensions["redis"], sentinel.client)

    def test_get_redis_returns_client_from_current_app(self):
        app = Flask(__name__)
        app.extensions["redis"] = sentinel.client

        with app.app_context():
            self.assertIs(get_redis(), sentinel.client)


if __name__ == "__main__":
    unittest.main()
