from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import json
import os
import time
import uuid
from importlib.util import find_spec
from urllib.parse import urlparse
from dotenv import load_dotenv


def _debug_log(hypothesis_id: str, message: str, data: dict):
    payload = {
        "sessionId": "9c8aad",
        "runId": "pre-fix",
        "hypothesisId": hypothesis_id,
        "id": f"log_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}",
        "location": "backend/app/db/session.py",
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    with open("debug-9c8aad.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")

load_dotenv()

# Thay đổi user, password, host, db_name phù hợp với máy của bạn
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
# region agent log
_debug_log(
    "H1",
    "DATABASE_URL presence and basic parse",
    {
        "has_database_url": SQLALCHEMY_DATABASE_URL is not None,
        "url_length": len(SQLALCHEMY_DATABASE_URL or ""),
    },
)
# endregion
parsed = urlparse(SQLALCHEMY_DATABASE_URL or "")
# region agent log
_debug_log(
    "H2",
    "DATABASE_URL parsed components",
    {
        "scheme": parsed.scheme,
        "host": parsed.hostname,
        "port": parsed.port,
        "db_name": parsed.path.lstrip("/") if parsed.path else "",
    },
)
# endregion
# region agent log
_debug_log(
    "H3",
    "Driver module availability",
    {
        "has_psycopg2": find_spec("psycopg2") is not None,
        "has_psycopg": find_spec("psycopg") is not None,
    },
)
# endregion
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # region agent log
    _debug_log(
        "H4",
        "create_engine success",
        {
            "engine_dialect": engine.dialect.name,
            "engine_driver": engine.dialect.driver,
        },
    )
    # endregion
except Exception as e:
    # region agent log
    _debug_log(
        "H4",
        "create_engine failure",
        {
            "error_type": type(e).__name__,
            "error_message": str(e),
        },
    )
    # endregion
    raise
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency để các API gọi DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()