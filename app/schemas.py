# schemas.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from typing import ClassVar
from graphene import ObjectType, String, Float, Int


class ProductSchema(ObjectType):
    """graphQL based schema

    Args:
        ObjectType (_type_): product
    """
    id = Int(required=True)
    part_number = String(required=True)
    branch_id = String(required=True)
    part_price = Float(required=True)
    short_desc = String(required=True)  
    createdat = String()
    updatedat = String()

class ProductBaseSchema(BaseModel):
    """pydantic based schema

    Args:
        BaseModel (_type_): product
    """
    id: Optional[str] = None
    part_number: str
    branch_id: str
    part_price: float
    short_desc: Optional[str] = None
    createdat: Optional[datetime] = None
    updatedat: Optional[datetime] = None
    
    config: ClassVar[ConfigDict] = {'populate_by_name': True}
    
class ListProductResponse(BaseModel):
    """
    pydantic based schema
    """
    status: str
    results: int
    products: List[dict]

        