from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True)
    merchant_name = Column(String)
    receipt_date = Column(Date)
    total_amount = Column(Float)
    tax_amount = Column(Float)
    currency = Column(String)

    items = relationship("ReceiptItem", back_populates="receipt")

class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    item_name = Column(String)
    quantity = Column(Float)
    unit_price = Column(Float)
    total_price = Column(Float)

    receipt = relationship("Receipt", back_populates="items")
