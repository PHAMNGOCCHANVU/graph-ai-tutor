from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Thay đổi user, password, host, db_name phù hợp với máy của bạn
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123456@localhost:5432/my_project_db"
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