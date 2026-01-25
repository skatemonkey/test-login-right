from datetime import timedelta


class Config:
    # JWT Configuration
    # TODO: In production, load this from environment variable
    JWT_SECRET_KEY = "your-super-secret-key-change-in-production"

    # Token expires in 30 minutes
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)