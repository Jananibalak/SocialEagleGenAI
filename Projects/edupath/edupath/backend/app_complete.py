from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database import Base, engine
from backend.routes.auth import auth_bp
from backend.routes.payments import payments_bp
from backend.routes.chat import chat_bp

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", "dev-secret")

# Create tables
Base.metadata.create_all(bind=engine)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(payments_bp, url_prefix='/api/payments')
app.register_blueprint(chat_bp, url_prefix='/api')

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
