from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import mysql.connector

DATABASE_URL = "mysql+pymysql://root:Info2026/*-@localhost:3306/fitpower_db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Info2026/*-",
        database="fitpower_db"
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()