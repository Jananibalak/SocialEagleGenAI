from sqlalchemy.orm import Session
from backend.models.user import User
from backend.models.token_transaction import TokenTransaction, TransactionType
from datetime import datetime
from typing import Tuple

class TokenManager:
    COSTS = {
        "chat_message": 1.0,
        "daily_checkin": 0.5,
        "session_analysis": 2.0,
        "progress_report": 5.0,
        "learning_path": 3.0
    }

    @staticmethod
    def get_balance(db: Session, user_id: int) -> float:
        user = db.query(User).filter(User.id == user_id).first()
        return user.token_balance if user else 0.0

    @staticmethod
    def has_sufficient_tokens(db: Session, user_id: int, action: str) -> Tuple[bool, float]:
        cost = TokenManager.COSTS.get(action, 1.0)
        balance = TokenManager.get_balance(db, user_id)
        return balance >= cost, cost

    @staticmethod
    def deduct_tokens(db: Session, user_id: int, action: str, description: str = None) -> Tuple[bool, str]:
        cost = TokenManager.COSTS.get(action, 1.0)

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return False, "User not found"

        if user.token_balance < cost:
            return False, f"Insufficient tokens. Need {cost}, have {user.token_balance}"

        user.token_balance -= cost

        transaction = TokenTransaction(
            user_id=user_id,
            type=TransactionType.USAGE,
            amount=-cost,
            balance_after=user.token_balance,
            description=description or f"Used for {action}",
            reference_id=action
        )

        db.add(transaction)
        db.commit()

        return True, f"Deducted {cost} tokens. Balance: {user.token_balance}"

    @staticmethod
    def add_tokens(db: Session, user_id: int, amount: float, transaction_type: TransactionType, description: str, payment_id: str = None) -> bool:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        user.token_balance += amount

        transaction = TokenTransaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount,
            balance_after=user.token_balance,
            description=description,
            payment_id=payment_id,
            payment_status="completed"
        )

        db.add(transaction)
        db.commit()

        return True
