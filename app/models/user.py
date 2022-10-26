from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

from ..database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    full_name = Column(String(32), nullable=False, server_default="Full Name")
    email = Column(String(64), nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    total_income = Column(Numeric(10, 2), nullable=False, server_default="0")
    total_expense = Column(Numeric(10, 2), nullable=False, server_default="0")

    currency = Column(String(3), nullable=False, server_default="USD")
    language = Column(String(2), nullable=False, server_default="en")

    def __repr__(self):
        return f'User(id={self.id}, full_name={self.full_name}, email={self.email})'
    