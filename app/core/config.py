import requests
from datetime import timedelta
from urllib.parse import quote_plus


def _get_db3_uri():
    """Fetch DB3 (test database) credentials from config API and build SQLAlchemy URI."""
    url = ("https://quant-platform.legenddigital.art/admin-api/system/custody/config"
           "?keys=custody.mysql.host,custody.mysql.port,"
           "custody.mysql.db3.database,custody.mysql.db3.username,custody.mysql.db3.password")
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        info = resp.json()["data"]
        host = info["custody.mysql.host"]
        port = info["custody.mysql.port"]
        user = quote_plus(info["custody.mysql.db3.username"])
        passwd = quote_plus(info["custody.mysql.db3.password"])
        db = info["custody.mysql.db3.database"]
        return f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset=utf8"
    except Exception as e:
        raise RuntimeError(f"Failed to fetch DB3 config: {e}")


class Config:
    # JWT Configuration
    # TODO: In production, load this from environment variable
    JWT_SECRET_KEY = "your-super-secret-key-change-in-production"

    # Token expires in 30 minutes
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=20)
    JWT_TOKEN_LOCATION = ["headers", "query_string"]
    JWT_QUERY_STRING_NAME = "access_token"
    JWT_QUERY_STRING_VALUE_PREFIX = ""

    # MySQL Database Configuration
    SQLALCHEMY_DATABASE_URI = _get_db3_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
