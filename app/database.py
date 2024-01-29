from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
DB_URI = os.getenv("DB_URI")

# Update the DATABASE_URL to use PostgreSQL
DATABASE_URL = DB_URI.replace("postgres://", "postgresql://")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def create_tables():
    # Create tables
    # Base.metadata.create_all(bind=engine)
    # alembic will create in this application
    pass

# Create tables when the application starts
create_tables()

def get_db():
    """In the context of FastAPI and dependency injection, when a route function depends on get_db, 
    FastAPI will execute get_db() to get a database session (db). 
    Using yield db allows FastAPI to provide the database session to the route function and ensure that 
    the session is properly closed (db.close()) after the route function finishes its execution.

    Yields:
        _type_: _description_
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        