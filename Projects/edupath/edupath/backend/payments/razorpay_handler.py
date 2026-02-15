import razorpay
import hmac
import hashlib
import os
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

logger = logging.getLogger(__name__)

class RazorpayHandler:
    @staticmethod
    def create_order_for_tokens(user_id: int, user_email: str, package_id: str) -> Dict:
        from backend.payments.plans import PricingPlans

        try:
            package = PricingPlans.get_package_by_id(package_id)

            notes = {
                "user_id": str(user_id),
                "user_email": user_email,
                "package_id": package_id,
                "tokens": str(package.actual_tokens),
                "type": "token_purchase"
            }

            order_data = {
                "amount": package.price_paise,
                "currency": "INR",
                "receipt": f"token_{user_id}_{int(datetime.now().timestamp())}",
                "notes": notes,
                "payment_capture": 1
            }

            order = razorpay_client.order.create(data=order_data)

            logger.info(f"Created order for user {user_id}: {order['id']}")

            return {
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "key_id": RAZORPAY_KEY_ID,
                "package_name": package.name,
                "package_tokens": package.actual_tokens
            }

        except razorpay.errors.BadRequestError as e:
            logger.error(f"Razorpay error: {e}")
            raise Exception(f"Payment system error: {str(e)}")

    @staticmethod
    def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
        try:
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            razorpay_client.utility.verify_payment_signature(params_dict)
            logger.info(f"Payment signature verified: {payment_id}")
            return True

        except razorpay.errors.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return False

    @staticmethod
    def verify_webhook_signature(payload: str, signature: str) -> bool:
        try:
            generated_signature = hmac.new(
                RAZORPAY_WEBHOOK_SECRET.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(generated_signature, signature)

        except Exception as e:
            logger.error(f"Webhook verification error: {e}")
            return False

    @staticmethod
    def handle_successful_payment(payment_id: str) -> bool:
        from shared.database import SessionLocal
        from backend.payments.token_manager import TokenManager
        from backend.models.token_transaction import TransactionType

        db = SessionLocal()

        try:
            payment = razorpay_client.payment.fetch(payment_id)
            order = razorpay_client.order.fetch(payment["order_id"])
            notes = order.get("notes", {})

            user_id = int(notes.get("user_id"))
            tokens = float(notes.get("tokens"))
            amount_rupees = payment["amount"] / 100

            success = TokenManager.add_tokens(
                db=db,
                user_id=user_id,
                amount=tokens,
                transaction_type=TransactionType.PURCHASE,
                description=f"Purchased {tokens} tokens (₹{amount_rupees})",
                payment_id=payment_id
            )

            if success:
                logger.info(f"Credited {tokens} tokens to user {user_id}")
                return True
            else:
                logger.error(f"Failed to credit tokens to user {user_id}")
                return False

        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return False

        finally:
            db.close()
