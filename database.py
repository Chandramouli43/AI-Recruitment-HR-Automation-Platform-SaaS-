# from sqlmodel import create_engine, Session
# import os
# # Example: adjust these values to match pgAdmin
# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql://postgres:admin@localhost:5432/signupdb"
# )

# engine = create_engine(DATABASE_URL, echo=True)

# def get_session():
#     with Session(engine) as session:
#         yield session


import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Replace these values with your PostgreSQL credentials
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "admin"
POSTGRES_DB = "signupdb"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL, echo=True)  # echo=True for debug logs

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    with Session(engine) as session:
        yield session
