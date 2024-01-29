# models.py
from sqlalchemy import Column, Integer, String, Boolean, Float, MetaData, Index, TIMESTAMP, DateTime
from sqlalchemy.sql import func
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    part_number = Column(String, index=True)
    branch_id = Column(String, index=True)
    part_price = Column(Float)
    short_desc = Column(String)
    createdat = Column(DateTime, default=func.now())
    updatedat = Column(DateTime, default=func.now(), onupdate=func.now())

    
    # Define an additional unique constraint for the combination of part_number and branch_id
    __table_args__ = (
        Index('ix_part_number_branch_id', 'part_number', 'branch_id', unique=True),
    )

    def __repr__(self):
        return f"<Product id={self.id}, part_number={self.part_number}, \
    branch_id={self.branch_id}, part_price={self.part_price}, \
    short_desc={self.short_desc}>"

    # (Optional) Add methods for manipulating or validating product data.

