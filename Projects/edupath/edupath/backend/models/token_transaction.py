from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from shared.database import Base
import enum

class TransactionType(enum.Enum):
    PURCHASE = "purchase"
    USAGE = "usage"
    REFUND = "refund"
    BONUS = "bonus"

class TokenTransaction(Base):
    __tablename__ = "token_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)

    type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)

    description = Column(String)
    reference_id = Column(String)

    payment_id = Column(String)
    payment_status = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
