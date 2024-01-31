# product.py
from fastapi import Depends, HTTPException, status, APIRouter, UploadFile, File
from sqlalchemy.orm import Session
from elasticsearch import Elasticsearch

import logging
from graphene import ObjectType, List, String, Schema

from database import get_db_graphql, get_db, DATABASE_URL
from crud import get_products
from celery_tasks import process_csv
import schemas


# Configure the logger (adjust settings as needed)
logging.basicConfig(filename='web.log', level=logging.ERROR)
logger = logging.getLogger(__name__)

# elasticsearch
es = Elasticsearch(hosts=["http://elasticsearch:9200"])

# Create "products" index
index_name = "products"

router = APIRouter(tags=["Products"], prefix="/products")

class Query(ObjectType):
    """GraphQl query class for resolver 

    Args:
        ObjectType (_type_): _description_

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    products = List(schemas.ProductSchema, skip=String(), limit=String(), part_number=String(), branch_id=String())
    
    async def resolve_products(self, info, skip: int = 0, limit: int = 10, part_number: str = None, branch_id = None):
        try:
            db = get_db_graphql() # get the DB session
            
            # Check if both part_number and branch_id are provided for filtering
            if part_number and branch_id:
                # Elasticsearch query to filter products based on part_number and branch_id
                es_query = {
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"part_number": part_number}},
                                {"match": {"branch_id": branch_id}}
                            ]
                        }
                    },
                    "size": limit  # Specify the limit for the number of results
                }
                logger.info(f"Elasticsearch query: {es_query}")

                # Execute the Elasticsearch query and retrieve the results
                es_result = es.search(index="products", body=es_query)
                logger.info(f"Elasticsearch result: {es_result}")

                # Extract the source data from Elasticsearch hits
                products = [hit["_source"] for hit in es_result["hits"]["hits"]]
                logger.info(f"Filtered products: {products}")
            else:
                # If no filtering parameters are provided, fetch all products using get_products from crud.py
                products = get_products(db, skip=skip, limit=limit)

            # Return the filtered or all products based on the conditions
            return products

        except ConnectionError as ce:
            logger.error("Connection error to Elasticsearch: %s", str(ce))
            raise HTTPException(status_code=500, detail="Error connecting to Elasticsearch. Check Elasticsearch status and connection details.")
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
    
# Schema attribute for GraphQL
schema = Schema(query=Query)
