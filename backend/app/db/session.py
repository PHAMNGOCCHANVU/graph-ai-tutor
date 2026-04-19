from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Thay đổi user, password, host, db_name phù hợp với máy của bạn
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/agi_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency để các API gọi DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()