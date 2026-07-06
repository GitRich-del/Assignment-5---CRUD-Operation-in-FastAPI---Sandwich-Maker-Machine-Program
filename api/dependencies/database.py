from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
from .config import conf


SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=conf.user,
    password=conf.password,
    host=conf.host,
    port=conf.port,
    database=conf.database,
    query={"charset": "utf8mb4"},
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()