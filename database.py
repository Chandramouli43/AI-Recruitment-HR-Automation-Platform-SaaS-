import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "admin"
POSTGRES_DB = "signupdb"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(bind=engine)  # for SQLModel tables
    Base.metadata.create_all(bind=engine)      # for SQLAlchemy tables
