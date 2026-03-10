from flask import current_app
import redis


def init_redis(app):
    app.extensions["redis"] = redis.Redis.from_url(
        app.config["REDIS_URL"],
        decode_responses=True,
    )


def get_redis():
    return current_app.extensions["redis"]
