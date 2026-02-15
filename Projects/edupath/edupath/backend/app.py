from flask import Flask
from flask_cors import CORS
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.config.mail_config import init_mail

app = Flask(__name__)

# ✅ CRITICAL: Configure CORS properly for all routes
CORS(app, 
     resources={r"/api/*": {
         "origins": ["http://localhost:8081", "http://localhost:3000", "http://127.0.0.1:8081"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True,
         "max_age": 3600
     }})

# Initialize email
init_mail(app)

# ✅ Register blueprints
from backend.routes.auth import auth_bp
from backend.routes.chat import chat_bp
from backend.routes.mentors import mentors_bp
from backend.routes.payments import payments_bp
from backend.routes.tokens import tokens_bp
from backend.routes.analytics import analytics_bp
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(mentors_bp, url_prefix='/api/mentors')
app.register_blueprint(payments_bp, url_prefix='/api/payments')
app.register_blueprint(tokens_bp, url_prefix='/api/tokens')

# ✅ Health check
@app.route('/health', methods=['GET'])
def health_check():
    return {"status": "healthy"}, 200

# ✅ CRITICAL: Global OPTIONS handler
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8081')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)