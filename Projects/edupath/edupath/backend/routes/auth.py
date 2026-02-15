from flask import Blueprint, request, jsonify
from backend.auth.jwt_handler import create_access_token
from backend.auth.password_handler import hash_password, verify_password, validate_password_strength
from backend.auth.rate_limiter import rate_limit
from backend.security.input_validator import InputValidator
from shared.database import SessionLocal
from backend.models.user import User
from backend.services.knowledge_graph import create_user_node
from backend.config.mail_config import generate_otp, send_otp_email, store_otp, verify_otp
import bcrypt
import os

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/login', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=300)
def login():
    """Login existing user"""
    db = None
    try:
        db = SessionLocal()
        data = request.json
        
        email = data.get('email')
        password = data.get('password')
        
        print(f"🔑 Login attempt: email={email}")
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        # Find user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # ✅ Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Update last active
        from datetime import datetime
        user.last_active = datetime.now()
        db.commit()
        
        # Create JWT token
        access_token = create_access_token(user.id,email)
        
        print(f"✅ User logged in: {user.username} (ID: {user.id})")
        
        return jsonify({
            "success": True,
            "access_token": access_token,
            "user_id": user.id,
            "username": user.username
        }), 200
        
    except Exception as e:
        if db:
            db.rollback()
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Login failed. Please try again."}), 500
    finally:
        if db:
            db.close()
    

# ✅ NEW: Send OTP endpoint
@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to email for verification"""
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email required"}), 400
        
        # Check if email already registered
        db = SessionLocal()
        existing_user = db.query(User).filter(User.email == email).first()
        db.close()
        
        if existing_user:
            return jsonify({"error": "Email already registered"}), 400
        
        # Generate and send OTP
        otp = generate_otp()
        
        # Store OTP
        store_otp(email, otp)
        
        # Send email
        if send_otp_email(email, otp):
            return jsonify({
                "success": True,
                "message": "OTP sent to your email"
            })
        else:
            return jsonify({"error": "Failed to send OTP. Please try again."}), 500
            
    except Exception as e:
        print(f"❌ Send OTP error: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ NEW: Verify OTP endpoint
@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp_endpoint():
    """Verify OTP code"""
    try:
        data = request.json
        email = data.get('email')
        otp = data.get('otp')
        
        if not email or not otp:
            return jsonify({"error": "Email and OTP required"}), 400
        
        # Verify OTP
        result = verify_otp(email, otp)
        
        if result['valid']:
            return jsonify({
                "success": True,
                "message": "Email verified successfully"
            })
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        print(f"❌ Verify OTP error: {e}")
        return jsonify({"error": str(e)}), 500

# UPDATE: Signup endpoint (require OTP verification)
@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Sign up new user (email must be verified via OTP first)"""
    db = None
    try:
        db = SessionLocal()
        data = request.json
        
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        full_name = data.get('full_name')
        otp_verified = data.get('otp_verified', False)
        
        print(f"📝 Signup attempt: email={email}, username={username}")
        
        # ✅ Validation
        if not email or not username or not password:
            return jsonify({"error": "Email, username, and password required"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        
        # ✅ Check OTP verification (can disable for testing)
        REQUIRE_OTP = os.getenv('REQUIRE_OTP', 'True').lower() == 'true'
        
        if REQUIRE_OTP and not otp_verified:
            return jsonify({"error": "Please verify your email with OTP first"}), 400
        
        # Check if user exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            return jsonify({"error": "Email already registered"}), 400
        
        existing_username = db.query(User).filter(User.username == username).first()
        if existing_username:
            return jsonify({"error": "Username already taken"}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # ✅ Create user - match EXACT model fields
        new_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password.decode('utf-8'),
            full_name=full_name or username,
            token_balance=50.0,  # ✅ Float not Integer
            total_sessions=0,
            total_learning_minutes=0,
            current_streak=0,
            longest_streak=0,
            mastery_score=0.0
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create JWT token
        access_token = create_access_token(new_user.id,email)
        
        print(f"✅ User created: {new_user.username} (ID: {new_user.id})")
        
        return jsonify({
            "success": True,
            "message": "Account created successfully",
            "access_token": access_token,
            "user_id": new_user.id,
            "username": new_user.username
        }), 201
        
    except Exception as e:
        if db:
            db.rollback()
        print(f"❌ Signup error: {e}")
        import traceback
        traceback.print_exc()
        
        # Return user-friendly error
        error_message = str(e)
        if 'duplicate key' in error_message.lower():
            return jsonify({"error": "Email or username already exists"}), 400
        elif 'invalid' in error_message.lower():
            return jsonify({"error": "Invalid input data"}), 400
        else:
            return jsonify({"error": "Failed to create account. Please try again."}), 500
    finally:
        if db:
            db.close()

