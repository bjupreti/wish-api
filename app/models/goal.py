from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Numeric
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from ..database import Base

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(512), nullable=False)
    price = Column(Numeric(10,2), nullable=False)
    # TODO: Ask to add "Add 13%<inputfield> tax" using checkbox in UI and ask frontend to handle this logic
    total_amount = Column(Numeric(10,2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User")