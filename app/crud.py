# crud.py
from datetime import datetime
import string
from sqlalchemy.exc import IntegrityError  # Import IntegrityError
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Product
from typing import List
from schemas import ProductBaseSchema  # Import ProductBaseSchema
from fastapi import HTTPException  # Import HTTPException
import logging


# Configure the logger (adjust settings as needed)
logging.basicConfig(filename='web.log', level=logging.ERROR)
logger = logging.getLogger(__name__)


def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    part_number: str = None, 
    branch_id: str = None
) -> List[dict]:
    """Retrieves a list of product dictionaries from the database.

    Args:
        db: SQLAlchemy session object.
        skip: Number of products to skip from the beginning of the result set.
            Defaults to 0.
        limit: Maximum number of products to return. Defaults to 10.
        part_number: Part number for querying a specific product. Defaults to None.
        branch_id: Branch ID for querying a specific product. Defaults to None.

    Returns:
        A list of product dictionaries, where each dictionary represents a product's attributes.
    """
    # Convert SQLAlchemy objects to dictionaries
    product_dicts = []
        
    # Check if it is for a particular product
    if part_number and branch_id:
        product = db.query(Product).filter(
            Product.part_number == part_number
        ).filter(
            Product.branch_id == branch_id
        ).first()
        if product:
            product_dict = {
                "id": product.id,
                "part_number": product.part_number,
                "branch_id": product.branch_id,
                "part_price": product.part_price,
                "short_desc": product.short_desc,
                "createdat": product.createdat,
                "updatedat": product.updatedat,
            }
            return [product_dict]
        else:
            return []
    else:
        # Query the database for products, applying pagination using offset and limit
        products = db.query(Product).offset(skip).limit(limit).all()
        
        product_dicts = [
            {
                "id": product.id,
                "part_number": product.part_number,
                "branch_id": product.branch_id,
                "part_price": product.part_price,
                "short_desc": product.short_desc,
                "createdat": product.createdat,
                "updatedat": product.updatedat,
            }
            for product in products
        ]
        
    return product_dicts


def insert_products_from_csv(db: Session, content: str):
    """Insert or update the products table from a CSV. 
    If the record already available then need to update, otherwise, it will be a new record and insert.

    Args:
        db: SQLAlchemy session object.
        content: CSV content as a string.
    """
    lines = content.strip().split('\n')
    header = lines[0].strip().split(',')

    for line in lines[1:]:  # Skip the header
        data = line.strip().split(',')
        row_dict = dict(zip(header, data))

        # Use ProductBaseSchema to validate each row
        product_data = ProductBaseSchema(**row_dict)

        # Convert Pydantic model to dictionary
        validated_data = product_data.dict()

        existing_product = (
            db.query(Product)
            .filter(Product.part_number == validated_data['part_number'])
            .filter(Product.branch_id == validated_data['branch_id'])
            .first()
        )
        
        # require to set createdat and updatedat col values
        current_datetime = datetime.utcnow()

        if existing_product:
            # Remove id from validated_data to prevent updating the id
            validated_data.pop('id', None)
            
            # Update existing record
            for key, value in validated_data.items():
                if key not in ['createdat', 'updatedat']:
                    setattr(existing_product, key, value)
            existing_product.updatedat = current_datetime
        else:
            # Insert new record along with createdat and updatedat
            validated_data['createdat'] = current_datetime
            validated_data['updatedat'] = current_datetime
            db_product = Product(**validated_data)
            # After creating the Product object, it is added to the SQLAlchemy session (db)
            db.add(db_product)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Integrity error during commit: {str(e)}")


