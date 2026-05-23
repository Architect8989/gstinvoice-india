from sqlalchemy import Column,Integer,String,Float,DateTime,Text
from app.database import Base
from datetime import datetime

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    client_name = Column(String(200), nullable=False)
    client_gstin = Column(String(20), default="")
    client_address = Column(Text, default="")
    description = Column(Text, nullable=False)
    hsn_code = Column(String(20), default="9983")
    amount = Column(Float, nullable=False)
    cgst = Column(Float, default=0.0)
    sgst = Column(Float, default=0.0)
    igst = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    gst_type = Column(String(20), default="cgst_sgst")
    place_of_supply = Column(String(100), default="")
    upi_id = Column(String(100), default="")
    status = Column(String(20), default="unpaid")
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
