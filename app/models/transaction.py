from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Numeric
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from ..database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(512), nullable=False)
    amount = Column(Numeric(10,2), nullable=False)
    # category = Column(Enum)
    category = Column(String(32), nullable=False)
    is_archived = Column(Boolean, nullable=False, server_default="False")
    is_income = Column(Boolean, nullable=False, server_default="False")
    is_expense = Column(Boolean, nullable=False, server_default="False")
    is_recurring = Column(Boolean, nullable=False, server_default="False")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    transaction_pic_url = Column(String(512), nullable=True, server_default="")
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User")