# celery_tasks.py
from celery import Celery
# Import CeleryConfig from the same directory level
import celery_config
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from crud import insert_products_from_csv
import logging


# Configure the logger (adjust settings as needed)
logging.basicConfig(filename='celery_tasks.log', level=logging.INFO)
logger = logging.getLogger(__name__)


celery = Celery(
    "tasks",
    broker=celery_config.CELERY_BROKER_URL,  # Use configured broker URL
    backend=celery_config.CELERY_RESULT_BACKEND  # Use configured result backend
)

@celery.task
def process_csv(db_url: str, content: str):
    try:
        # Create a new session using the provided database information
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        try:
            # Call the insert_products_from_csv function with the new session
            insert_products_from_csv(db, content)
            db.commit()  # Commit the changes to the database
        except Exception as e:
            db.rollback()  # Rollback changes in case of errors
            raise e  # Re-raise the exception for proper handling
        finally:
            db.close()  # Close the session to release resources
        return "CSV processing completed successfully"
    except Exception as e:
        # Log or handle any errors that occur during task execution
        logger.error("Error processing CSV: %s", str(e))
        return f"Error processing CSV: {str(e)}"
