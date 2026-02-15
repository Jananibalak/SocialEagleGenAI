# ✅ FIX #1: BACKEND - Update Token Packages with New Pricing

# File: backend/routes/tokens.py

from flask import Blueprint, request, jsonify
from backend.auth.jwt_handler import require_auth
from backend.payments.token_manager import TokenManager
from shared.database import SessionLocal
from backend.models.user import User
import os

tokens_bp = Blueprint('tokens', __name__)
token_manager = TokenManager()

# ✅ NEW PRICING STRUCTURE
TOKEN_PACKAGES = [
    {
        'id': 'starter_pack',
        'name': 'Starter Pack',
        'actual_tokens': 50,
        'bonus_tokens': 0,
        'price': 175,
        'bonus_percentage': 0,
    },
    {
        'id': 'power_pack',
        'name': 'Power Pack',
        'actual_tokens': 100,
        'bonus_tokens': 0,
        'price': 300,
        'bonus_percentage': 0,
    },
    {
        'id': 'mega_pack',
        'name': 'Mega Pack',
        'actual_tokens': 200,
        'bonus_tokens': 0,
        'price': 500,
        'bonus_percentage': 0,
    },
]

@tokens_bp.route('/packages', methods=['GET'])
def get_token_packages():
    """Get available token packages"""
    try:
        return jsonify({
            'token_packages': TOKEN_PACKAGES,
            'packages': TOKEN_PACKAGES  # ✅ Both formats for compatibility
        }), 200
    except Exception as e:
        print(f"❌ Error getting packages: {e}")
        return jsonify({'error': str(e)}), 500

@tokens_bp.route('/balance', methods=['GET'])
@require_auth
def get_balance():
    """Get user's token balance"""
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == request.user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'balance': user.token_balance or 0,
            'user_id': user.id
        }), 200
    except Exception as e:
        print(f"❌ Error getting balance: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@tokens_bp.route('/create-order', methods=['POST'])
@require_auth
def create_token_order():
    """Create Razorpay order for token purchase"""
    try:
        data = request.json
        package_id = data.get('package_id')
        
        if not package_id:
            return jsonify({'error': 'Package ID required'}), 400
        
        # Find package
        package = next((p for p in TOKEN_PACKAGES if p['id'] == package_id), None)
        
        if not package:
            return jsonify({'error': 'Invalid package ID'}), 400
        
        db = SessionLocal()
        user = db.query(User).filter(User.id == request.user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create Razorpay order
        order_data = token_manager.create_order(
            user_id=user.id,
            package_id=package_id,
            amount=package['price'],
            tokens=package['actual_tokens'] + package['bonus_tokens']
        )
        
        return jsonify(order_data), 200
        
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        if 'db' in locals():
            db.close()

@tokens_bp.route('/verify-payment', methods=['POST'])
@require_auth
def verify_payment():
    """Verify Razorpay payment and add tokens"""
    try:
        data = request.json
        
        payment_id = data.get('payment_id')
        order_id = data.get('order_id')
        signature = data.get('signature')
        
        if not all([payment_id, order_id, signature]):
            return jsonify({'error': 'Missing payment data'}), 400
        
        # Verify payment
        result = token_manager.verify_payment(
            payment_id=payment_id,
            order_id=order_id,
            signature=signature,
            user_id=request.user_id
        )
        
        if result['success']:
            # Reload user balance
            db = SessionLocal()
            user = db.query(User).filter(User.id == request.user_id).first()
            
            return jsonify({
                'success': True,
                'message': 'Payment successful!',
                'new_balance': user.token_balance
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Payment verification failed')
            }), 400
            
    except Exception as e:
        print(f"❌ Error verifying payment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        if 'db' in locals():
            db.close()