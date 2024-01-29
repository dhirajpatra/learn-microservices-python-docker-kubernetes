# product.py
import schemas
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, UploadFile, File
from database import get_db, DATABASE_URL
from crud import get_products
from celery_tasks import process_csv
import logging
from graphene import ObjectType, Schema, String, List


# Configure the logger (adjust settings as needed)
logging.basicConfig(filename='web.log', level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Products"], prefix="/products")

class Query(ObjectType):
    products = List(schemas.ProductSchema, skip=String(), limit=String())
    
    async def resolve_products(self, info, skip: int = 0, limit: int = 10, db=Depends(get_db)):
        try:
            # calling from crud.py
            products = get_products(db, skip=skip, limit=limit)
            return products
        except Exception as e:
            logger.error("Error processing products db: %s", str(e))
            raise HTTPException(status_code=500, detail=str(e))
           

# @router.get("/", response_model=List[dict], status_code=status.HTTP_200_OK)
@router.get("", status_code=status.HTTP_200_OK)
async def get_products_list(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        products = get_products(db, skip=skip, limit=limit)
        
        # # Convert the list of Pydantic models to a list of dictionaries
        # products_dict_list = [product.dict() for product in products]
        
        # create an instance of ListProductResponse using the retrieved products
        response = schemas.ListProductResponse(
            status="Success",
            results=len(products),
            products=products
        )
        # return products
        # return [{key: value for key, value in product.items() 
        #         if not key.startswith('_')} for product in products]
        
        # return the response using the ListProductResponse
        return response
    except Exception as e:
        # Log or handle any errors that occur during task execution
        logger.error("Error processing products db: %s", str(e))

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    This API method will push the work upload file for celery

    Args:
        file (UploadFile, optional): _description_. Defaults to File(...).
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    try:
        content = await file.read()
        content_str = content.decode('utf-8')

        # Use the DATABASE_URL directly for Celery task
        process_csv.delay(DATABASE_URL, content_str)

        return {"message": "File uploaded successfully"}
    except Exception as e:
        logger.error("Error processing CSV: %s", str(e)) 
        raise HTTPException(status_code=500, detail=str(e))