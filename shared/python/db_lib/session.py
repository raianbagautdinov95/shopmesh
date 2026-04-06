from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass

def build_session_factory(database_url: str):
    engine = create_engine(database_url, future=True, pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
