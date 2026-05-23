from sqlalchemy import create_engine, Column,Integer,String,Float,DateTime,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DB_PATH = os.environ.get("DATABASE_URL","sqlite:///./gstinvoice.db")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False}) if DB_PATH.startswith("sqlite") else create_engine(DB_PATH)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
