from flask import Blueprint, request, jsonify
from backend.auth.jwt_handler import require_auth
from backend.auth.rate_limiter import rate_limit
from backend.payments.razorpay_handler import RazorpayHandler
from backend.payments.plans import PricingPlans
from backend.payments.token_manager import TokenManager
from shared.database import SessionLocal

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/plans', methods=['GET'])
def get_plans():
    return jsonify({
        "packages": [
            {
                "id": pkg.id,
                "name": pkg.name,
                "tokens": pkg.tokens,
                "total_tokens": pkg.actual_tokens,
                "price": pkg.price_display,
                "price_paise": pkg.price_paise
            }
            for pkg in PricingPlans.TOKEN_PACKAGES
        ]
    })

@payments_bp.route('/create-order/tokens', methods=['POST'])
@require_auth
@rate_limit(max_requests=10, window_seconds=300)
def create_order():
    try:
        data = request.json
        package_id = data.get('package_id')

        if not package_id:
            return jsonify({"error": "package_id required"}), 400

        order = RazorpayHandler.create_order_for_tokens(
            user_id=request.user_id,
            user_email=request.user_email,
            package_id=package_id
        )

        return jsonify(order)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@payments_bp.route('/verify-payment', methods=['POST'])
@require_auth
def verify_payment():
    try:
        data = request.json
        order_id = data.get('order_id')
        payment_id = data.get('payment_id')
        signature = data.get('signature')

        if not all([order_id, payment_id, signature]):
            return jsonify({"error": "Missing fields"}), 400

        is_valid = RazorpayHandler.verify_payment_signature(
            order_id, payment_id, signature
        )

        if not is_valid:
            return jsonify({"error": "Invalid signature"}), 400

        success = RazorpayHandler.handle_successful_payment(payment_id)

        if success:
            db = SessionLocal()
            balance = TokenManager.get_balance(db, request.user_id)
            db.close()

            return jsonify({
                "success": True,
                "new_balance": balance
            })
        else:
            return jsonify({"error": "Payment processing failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@payments_bp.route('/balance', methods=['GET'])
@require_auth
def get_balance():
    try:
        db = SessionLocal()
        balance = TokenManager.get_balance(db, request.user_id)
        db.close()

        return jsonify({"balance": balance})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
