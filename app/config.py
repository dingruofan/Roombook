import os
from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"缺少必要环境变量: {name}")
    return value


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://"
        f"{_require_env('MYSQL_USER')}:"
        f"{_require_env('MYSQL_PASSWORD')}@"
        f"{_require_env('MYSQL_HOST')}:"
        f"{_require_env('MYSQL_PORT')}/"
        f"{_require_env('MYSQL_DB')}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False