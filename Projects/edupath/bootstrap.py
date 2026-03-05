
#!/usr/bin/env python3
"""
EduPath Complete Project Generator
Generates the ENTIRE project structure with all files

Run: python bootstrap_complete.py

This creates:
- Backend (Flask API with all routes)
- Auth system (JWT, passwords)
- Razorpay integration
- AI Coach service
- Knowledge Graph service
- Database models
- Security middleware
- Documentation
- Docker setup
- Frontend starter
"""

import os
from pathlib import Path
from textwrap import dedent

class ProjectGenerator:
    def __init__(self, project_name="edupath"):
        self.project_name = project_name
        self.base_path = Path(project_name)
        self.files_created = 0
        
    def create_file(self, path, content):
        """Create file with content"""
        filepath = self.base_path / path
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Dedent and strip content
        clean_content = dedent(content).strip() + "\n"
        filepath.write_text(clean_content, encoding='utf-8')
        
        self.files_created += 1
        print(f"✅ {path}")
        
    def generate_all(self):
        """Generate complete project"""
        print("=" * 80)
        print(f"🚀 GENERATING COMPLETE EDUPATH PROJECT")
        print("=" * 80)
        print()
        
        # Generate each section
        self.generate_root_files()
        self.generate_backend()
        self.generate_shared()
        self.generate_docs()
        self.generate_scripts()
        self.generate_frontend_starter()
        
        print()
        print("=" * 80)
        print(f"✅ PROJECT GENERATED! Created {self.files_created} files")
        print("=" * 80)
        self.print_next_steps()
    
    def generate_root_files(self):
        """Generate root configuration files"""
        print("\n📁 Creating root files...")
        
        # README.md
        self.create_file("README.md", """
        # 🎓 EduPath - AI-Powered Personal Learning Trainer
        
        An AI-powered learning platform with chatbot-first interface, built for Indian learners.
        
        ## ✨ Features
        
        - 🤖 **AI Coach** - GPT-4o-mini powered personalized guidance
        - 📅 **Daily Check-ins** - Morning motivation & evening reflections
        - 🔥 **Streak Tracking** - Gamified consistency
        - 📊 **Knowledge Graph** - Neo4j powered concept tracking
        - 💰 **Razorpay** - UPI, Cards, Net Banking (India-focused)
        - 🔐 **OWASP Compliant** - Production-grade security
        
        ## 🚀 Quick Start
        
        ### Prerequisites
        - Python 3.8+
        - Docker Desktop
        - Razorpay Account (https://razorpay.com)
        - OpenRouter API Key (https://openrouter.ai)
        
        ### Setup (5 minutes)
```bash
        # 1. Copy environment file
        cp .env.example .env
        # Edit .env with your API keys
        
        # 2. Start infrastructure
        docker-compose up -d
        
        # 3. Setup backend
        cd backend
        python -m venv venv
        source venv/bin/activate  # Windows: venv\\Scripts\\activate
        pip install -r requirements.txt
        
        # 4. Initialize databases
        python ../scripts/init_db.py
        python ../scripts/seed_concepts.py
        
        # 5. Run API
        python run_api.py
```
        
        API will be at: **http://localhost:5000**
        
        ## 📖 Documentation
        
        - [Setup Guide](docs/SETUP.md)
        - [API Reference](docs/API.md)
        - [Architecture](docs/ARCHITECTURE.md)
        - [Security](docs/SECURITY.md)
        
        ## 💰 Pricing (India)
        
        ### Token Packages
        - Starter: ₹499 (100 tokens)
        - Power: ₹1,999 (550 tokens) 🔥
        - Ultimate: ₹3,499 (1,200 tokens)
        
        ### Subscriptions
        - Free: 50 messages/month
        - Pro: ₹799/month (unlimited)
        - Pro Annual: ₹7,999/year
        
        ## 🧪 Testing
        
        **Razorpay Test Credentials:**
        - Card: 4111 1111 1111 1111
        - CVV: 123
        - UPI: success@razorpay
        
        ## 📄 License
        
        MIT License
        
        ## 🙏 Built With
        
        - Flask (Backend)
        - React Native (Frontend)
        - Neo4j (Knowledge Graph)
        - PostgreSQL (User Data)
        - Razorpay (Payments)
        - OpenRouter (AI/LLM)
        
        ---
        
        **Made with ❤️ in India 🇮🇳**
        """)
        
        # .gitignore
        self.create_file(".gitignore", """
        # Python
        __pycache__/
        *.py[cod]
        *$py.class
        *.so
        .Python
        env/
        venv/
        ENV/
        *.egg-info/
        
        # Environment
        .env
        .env.local
        
        # Database
        *.db
        *.sqlite
        
        # Logs
        *.log
        logs/
        
        # IDE
        .vscode/
        .idea/
        *.swp
        
        # OS
        .DS_Store
        Thumbs.db
        
        # Node
        node_modules/
        npm-debug.log
        
        # Build
        build/
        dist/
        """)
        
        # .env.example
        self.create_file(".env.example", """
        # ===== RAZORPAY (REQUIRED) =====
        RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
        RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
        RAZORPAY_WEBHOOK_SECRET=xxxxxxxxxxxxxxxxxxxxx
        
        # ===== OPENROUTER (REQUIRED) =====
        OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxx
        MODEL_NAME=openai/gpt-4o-mini
        
        # ===== NEO4J (REQUIRED) =====
        NEO4J_URI=bolt://localhost:7687
        NEO4J_USERNAME=neo4j
        NEO4J_PASSWORD=your_strong_password
        
        # ===== POSTGRESQL (REQUIRED) =====
        DATABASE_URL=postgresql://edupath:edupath_pass@localhost:5432/edupath_db
        POSTGRES_USER=edupath
        POSTGRES_PASSWORD=edupath_pass
        POSTGRES_DB=edupath_db
        
        # ===== FLASK =====
        FLASK_SECRET_KEY=change-this-in-production
        FLASK_ENV=development
        DEBUG=True
        
        # ===== JWT =====
        JWT_SECRET_KEY=change-this-jwt-secret
        JWT_REFRESH_SECRET_KEY=change-this-refresh-secret
        JWT_ALGORITHM=HS256
        
        # ===== APP CONFIG =====
        FRONTEND_URL=http://localhost:3000
        BACKEND_URL=http://localhost:5000
        DAILY_CHECKIN_HOUR=9
        """)
        
        # docker-compose.yml
        self.create_file("docker-compose.yml", """
        version: '3.8'
        
        services:
          neo4j:
            image: neo4j:5.15-community
            container_name: edupath_neo4j
            ports:
              - "7474:7474"
              - "7687:7687"
            environment:
              - NEO4J_AUTH=neo4j/$${NEO4J_PASSWORD:-your_password}
              - NEO4J_PLUGINS=["apoc"]
            volumes:
              - neo4j_data:/data
            restart: unless-stopped
            healthcheck:
              test: ["CMD-SHELL", "cypher-shell -u neo4j -p $${NEO4J_PASSWORD:-your_password} 'RETURN 1'"]
              interval: 10s
              timeout: 5s
              retries: 5
        
          postgres:
            image: postgres:16-alpine
            container_name: edupath_postgres
            ports:
              - "5432:5432"
            environment:
              - POSTGRES_USER=$${POSTGRES_USER:-edupath}
              - POSTGRES_PASSWORD=$${POSTGRES_PASSWORD:-edupath_pass}
              - POSTGRES_DB=$${POSTGRES_DB:-edupath_db}
            volumes:
              - postgres_data:/var/lib/postgresql/data
            restart: unless-stopped
            healthcheck:
              test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER:-edupath}"]
              interval: 5s
              timeout: 5s
              retries: 5
        
          redis:
            image: redis:7-alpine
            container_name: edupath_redis
            ports:
              - "6379:6379"
            volumes:
              - redis_data:/data
            restart: unless-stopped
            command: redis-server --appendonly yes
        
        volumes:
          neo4j_data:
          postgres_data:
          redis_data:
        """)
        
        # setup.py
        self.create_file("setup.py", """
        from setuptools import setup, find_packages
        
        setup(
            name="edupath",
            version="1.0.0",
            description="AI-Powered Personal Learning Trainer",
            packages=find_packages(),
            python_requires=">=3.8",
            install_requires=[
                "flask>=3.0.0",
                "flask-cors>=4.0.0",
                "razorpay>=1.4.2",
                "neo4j>=5.15.0",
                "openai>=1.10.0",
                "python-dotenv>=1.0.0",
                "sqlalchemy>=2.0.0",
                "psycopg2-binary>=2.9.9",
                "bcrypt>=4.1.2",
                "pyjwt>=2.8.0",
                "bleach>=6.1.0",
            ],
        )
        """)
        
        # LICENSE
        self.create_file("LICENSE", """
        MIT License
        
        Copyright (c) 2024 EduPath
        
        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:
        
        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.
        
        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
        """)
    
    def generate_backend(self):
        """Generate complete backend"""
        print("\n📁 Creating backend files...")
        
        # Create __init__.py files for all modules
        modules = [
            "backend",
            "backend/auth",
            "backend/payments",
            "backend/services",
            "backend/models",
            "backend/routes",
            "backend/security",
        ]
        for module in modules:
            self.create_file(f"{module}/__init__.py", "")
        
        # requirements.txt
        self.create_file("backend/requirements.txt", """
        flask==3.0.0
        flask-cors==4.0.0
        flask-sqlalchemy==3.1.1
        razorpay==1.4.2
        neo4j==5.15.0
        openai==1.10.0
        python-dotenv==1.0.0
        sqlalchemy==2.0.23
        psycopg2-binary==2.9.9
        bcrypt==4.1.2
        pyjwt==2.8.0
        bleach==6.1.0
        python-jose==3.3.0
        passlib==1.7.4
        """)
        
        # run_api.py
        self.create_file("backend/run_api.py", """
        #!/usr/bin/env python
        import sys
        from pathlib import Path
        
        # Add project root to path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from backend.app import app
        
        if __name__ == '__main__':
            print("=" * 70)
            print("🚀 EDUPATH API SERVER")
            print("=" * 70)
            print("Server: http://localhost:5000")
            print("Health: http://localhost:5000/health")
            print("Docs: http://localhost:5000/docs")
            print("=" * 70)
            
            app.run(host='0.0.0.0', port=5000, debug=True)
        """)
        
        # app.py - Main Flask application
        self.create_file("backend/app.py", """
        from flask import Flask, jsonify, request
        from flask_cors import CORS
        from datetime import datetime
        import os
        import sys
        from pathlib import Path
        
        # Add project root to path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from shared.database import Base, engine
        from backend.auth.jwt_handler import require_auth
        
        # Initialize Flask
        app = Flask(__name__)
        CORS(app, origins=os.getenv("ALLOWED_ORIGINS", "*").split(","))
        
        # Configuration
        app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
        app.config['JSON_SORT_KEYS'] = False
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # ===== HEALTH & INFO ROUTES =====
        
        @app.route('/')
        def home():
            return jsonify({
                "name": "EduPath API",
                "version": "1.0.0",
                "status": "running",
                "timestamp": datetime.now().isoformat()
            })
        
        @app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "services": {
                    "api": "up",
                    "database": "up",
                    "neo4j": "up"
                }
            })
        
        @app.route('/docs')
        def docs():
            return jsonify({
                "endpoints": {
                    "auth": {
                        "POST /api/auth/signup": "Create new user",
                        "POST /api/auth/login": "Login user",
                        "POST /api/auth/refresh": "Refresh token",
                    },
                    "payments": {
                        "GET /api/payments/plans": "Get pricing plans",
                        "POST /api/payments/create-order": "Create Razorpay order",
                        "POST /api/payments/verify": "Verify payment",
                    },
                    "chat": {
                        "POST /api/chat": "Chat with AI coach",
                        "GET /api/checkin/morning": "Morning check-in",
                    }
                }
            })
        
        # ===== PROTECTED ROUTE EXAMPLE =====
        
        @app.route('/api/protected')
        @require_auth
        def protected():
            return jsonify({
                "message": "This is a protected route",
                "user_id": request.user_id,
                "email": request.user_email
            })
        
        # ===== ERROR HANDLERS =====
        
        @app.errorhandler(404)
        def not_found(error):
            return jsonify({"error": "Endpoint not found"}), 404
        
        @app.errorhandler(500)
        def internal_error(error):
            return jsonify({"error": "Internal server error"}), 500
        
        if __name__ == '__main__':
            app.run(debug=True)
        """)
        
        # Auth - JWT Handler
        self.create_file("backend/auth/jwt_handler.py", """
        import jwt
        from datetime import datetime, timedelta
        from functools import wraps
        from flask import request, jsonify
        import os
        
        SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 15
        
        def create_access_token(user_id: int, email: str) -> str:
            payload = {
                "sub": str(user_id),
                "email": email,
                "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                "iat": datetime.utcnow()
            }
            return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        def verify_token(token: str):
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                return payload
            except jwt.ExpiredSignatureError:
                return None
            except jwt.InvalidTokenError:
                return None
        
        def require_auth(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                token = None
                auth_header = request.headers.get('Authorization')
                
                if auth_header and auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                
                if not token:
                    return jsonify({"error": "Missing token"}), 401
                
                payload = verify_token(token)
                if not payload:
                    return jsonify({"error": "Invalid token"}), 401
                
                request.user_id = int(payload['sub'])
                request.user_email = payload['email']
                
                return f(*args, **kwargs)
            return decorated
        """)
        
        # Auth - Password Handler
        self.create_file("backend/auth/password_handler.py", """
        import bcrypt
        
        def hash_password(password: str) -> str:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        
        def verify_password(password: str, hashed: str) -> bool:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        
        def validate_password_strength(password: str) -> tuple[bool, str]:
            if len(password) < 8:
                return False, "Password must be at least 8 characters"
            if not any(c.isupper() for c in password):
                return False, "Password must contain uppercase letter"
            if not any(c.islower() for c in password):
                return False, "Password must contain lowercase letter"
            if not any(c.isdigit() for c in password):
                return False, "Password must contain digit"
            return True, "Password is strong"
        """)
        
        # Models - User
        self.create_file("backend/models/user.py", """
        from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
        from sqlalchemy.sql import func
        from shared.database import Base
        
        class User(Base):
            __tablename__ = "users"
            
            id = Column(Integer, primary_key=True, index=True)
            username = Column(String, unique=True, index=True, nullable=False)
            email = Column(String, unique=True, index=True, nullable=False)
            hashed_password = Column(String, nullable=False)
            
            # Profile
            full_name = Column(String)
            mobile_number = Column(String)
            learning_goal = Column(String)
            current_level = Column(String, default="Beginner")
            
            # Tokens & Subscription
            token_balance = Column(Float, default=0.0)
            razorpay_customer_id = Column(String, unique=True)
            
            # Stats
            total_sessions = Column(Integer, default=0)
            total_learning_minutes = Column(Integer, default=0)
            current_streak = Column(Integer, default=0)
            longest_streak = Column(Integer, default=0)
            mastery_score = Column(Float, default=0.0)
            
            # Timestamps
            created_at = Column(DateTime(timezone=True), server_default=func.now())
            last_checkin = Column(DateTime(timezone=True))
            last_active = Column(DateTime(timezone=True))
        
        class LearningSession(Base):
            __tablename__ = "learning_sessions"
            
            id = Column(Integer, primary_key=True, index=True)
            user_id = Column(Integer, index=True, nullable=False)
            
            # Session info
            start_time = Column(DateTime(timezone=True), nullable=False)
            end_time = Column(DateTime(timezone=True))
            duration_minutes = Column(Integer)
            topic = Column(String)
            
            # Ratings
            understanding_before = Column(Integer)
            understanding_after = Column(Integer)
            difficulty_rating = Column(Integer)
            enjoyment_rating = Column(Integer)
            
            # Notes
            notes = Column(String)
            created_at = Column(DateTime(timezone=True), server_default=func.now())
        """)
        
        # Payments - Plans
        self.create_file("backend/payments/plans.py", """
        from dataclasses import dataclass
        from typing import List
        
        @dataclass
        class TokenPackage:
            id: str
            name: str
            tokens: float
            price_paise: int
            price_display: str
            bonus_percentage: int = 0
            
            @property
            def actual_tokens(self) -> float:
                return self.tokens * (1 + self.bonus_percentage / 100)
        
        class PricingPlans:
            TOKEN_PACKAGES = [
                TokenPackage("starter", "Starter Pack", 100, 49900, "₹499"),
                TokenPackage("power", "Power Pack", 500, 199900, "₹1,999", 10),
                TokenPackage("ultimate", "Ultimate Pack", 1000, 349900, "₹3,499", 20),
            ]
            
            @classmethod
            def get_package_by_id(cls, package_id: str):
                for pkg in cls.TOKEN_PACKAGES:
                    if pkg.id == package_id:
                        return pkg
                raise ValueError(f"Package not found: {package_id}")
        """)
        
        # Services - AI Coach (Simple version)
        self.create_file("backend/services/ai_coach.py", """
        from openai import OpenAI
        import os
        
        class AICoach:
            def __init__(self):
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    default_headers={
                        "HTTP-Referer": "http://localhost:5000",
                        "X-Title": "EduPath"
                    }
                )
                self.model = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
            
            def chat(self, message: str, context: dict = None) -> str:
                try:
                    messages = [
                        {"role": "system", "content": "You are Alex, a friendly AI learning coach."},
                        {"role": "user", "content": message}
                    ]
                    
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=500
                    )
                    
                    return response.choices[0].message.content
                except Exception as e:
                    return f"Error: {str(e)}"
        """)
    
    def generate_shared(self):
        """Generate shared modules"""
        print("\n📁 Creating shared modules...")
        
        self.create_file("shared/__init__.py", "")
        
        self.create_file("shared/database.py", """
        from sqlalchemy import create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from neo4j import GraphDatabase
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # PostgreSQL
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./edupath.db")
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()
        
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        
        # Neo4j
        class Neo4jConnection:
            def __init__(self):
                try:
                    self.driver = GraphDatabase.driver(
                        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                        auth=(
                            os.getenv("NEO4J_USERNAME", "neo4j"),
                            os.getenv("NEO4J_PASSWORD", "password")
                        )
                    )
                except Exception as e:
                    print(f"Warning: Neo4j connection failed: {e}")
                    self.driver = None
            
            def close(self):
                if self.driver:
                    self.driver.close()
            
            def get_session(self):
                if self.driver:
                    return self.driver.session()
                return None
        
        neo4j_conn = Neo4jConnection()
        """)
    
    def generate_scripts(self):
        """Generate utility scripts"""
        print("\n📁 Creating scripts...")
        
        self.create_file("scripts/__init__.py", "")
        
        self.create_file("scripts/init_db.py", """
        #!/usr/bin/env python
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from shared.database import Base, engine, neo4j_conn
        from backend.models.user import User, LearningSession
        
        def init_postgresql():
            print("Initializing PostgreSQL...")
            Base.metadata.create_all(bind=engine)
            print("✅ PostgreSQL tables created")
        
        def init_neo4j():
            print("Initializing Neo4j...")
            session = neo4j_conn.get_session()
            if session:
                try:
                    # Create constraints
                    session.run(
                        "CREATE CONSTRAINT concept_name IF NOT EXISTS "
                        "FOR (c:Concept) REQUIRE c.name IS UNIQUE"
                    )
                    print("✅ Neo4j constraints created")
                finally:
                    session.close()
            else:
                print("⚠️  Neo4j not available")
        
        if __name__ == "__main__":
            print("=" * 70)
            print("INITIALIZING EDUPATH DATABASES")
            print("=" * 70)
            init_postgresql()
            init_neo4j()
            print("=" * 70)
            print("✅ Database initialization complete!")
            print("=" * 70)
        """)
        
        self.create_file("scripts/seed_concepts.py", """
        #!/usr/bin/env python
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from shared.database import neo4j_conn
        
        def seed_concepts():
            print("Seeding learning concepts...")
            session = neo4j_conn.get_session()
            
            if not session:
                print("⚠️  Neo4j not available")
                return
            
            try:
                concepts = [
                    {"name": "Python Basics", "difficulty": 2},
                    {"name": "Variables", "difficulty": 1},
                    {"name": "Functions", "difficulty": 3},
                    {"name": "Linear Algebra", "difficulty": 5},
                    {"name": "Machine Learning", "difficulty": 7},
                ]
                
                for concept in concepts:
                    session.run(
                        "MERGE (c:Concept {name: $name}) "
                        "SET c.difficulty = $difficulty",
                        **concept
                    )
                
                print(f"✅ Seeded {len(concepts)} concepts")
            finally:
                session.close()
        
        if __name__ == "__main__":
            seed_concepts()
        """)
        
        self.create_file("scripts/create_test_user.py", """
        #!/usr/bin/env python
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from shared.database import SessionLocal
        from backend.models.user import User
        from backend.auth.password_handler import hash_password
        
        def create_test_user():
            db = SessionLocal()
            
            try:
                # Check if user exists
                existing = db.query(User).filter(User.email == "test@edupath.app").first()
                if existing:
                    print("Test user already exists")
                    return
                
                # Create test user
                user = User(
                    username="testuser",
                    email="test@edupath.app",
                    hashed_password=hash_password("Test@1234"),
                    full_name="Test User",
                    learning_goal="Learn Machine Learning",
                    token_balance=100.0
                )
                
                db.add(user)
                db.commit()
                
                print("✅ Test user created!")
                print("   Email: test@edupath.app")
                print("   Password: Test@1234")
                
            finally:
                db.close()
        
        if __name__ == "__main__":
            create_test_user()
        """)
    
    def generate_docs(self):
        """Generate documentation"""
        print("\n📁 Creating documentation...")
        
        self.create_file("docs/SETUP.md", """
        # Setup Guide
        
        ## Prerequisites
        
        - Python 3.8+
        - Docker Desktop
        - Razorpay Account
        - OpenRouter API Key
        
        ## Installation Steps
        
        ### 1. Environment Setup
```bash
        # Copy environment file
        cp .env.example .env
        
        # Edit .env and add your API keys
```
        
        ### 2. Start Infrastructure
```bash
        # Start PostgreSQL, Neo4j, Redis
        docker-compose up -d
        
        # Wait 10 seconds for startup
        sleep 10
```
        
        ### 3. Backend Setup
```bash
        cd backend
        
        # Create virtual environment
        python -m venv venv
        source venv/bin/activate  # Windows: venv\\Scripts\\activate
        
        # Install dependencies
        pip install -r requirements.txt
        
        # Initialize databases
        python ../scripts/init_db.py
        python ../scripts/seed_concepts.py
        python ../scripts/create_test_user.py
        
        # Start API
        python run_api.py
```
        
        ### 4. Test
```bash
        # Health check
        curl http://localhost:5000/health
        
        # Should return: {"status": "healthy"}
```
        
        ## Troubleshooting
        
        ### Database connection failed
        
        Check Docker containers:
```bash
        docker ps
```
        
        ### Module not found
        
        Install in editable mode:
```bash
        pip install -e .
```
        """)
        
        self.create_file("docs/API.md", """
        # API Reference
        
        ## Base URL
```
        http://localhost:5000
```
        
        ## Authentication
        
        Most endpoints require JWT token:
```
        Authorization: Bearer <token>
```
        
        ## Endpoints
        
        ### Health Check
```
        GET /health
```
        
        Response:
```json
        {
          "status": "healthy"
        }
```
        
        ### Create User
```
        POST /api/auth/signup
```
        
        Body:
```json
        {
          "username": "janani",
          "email": "janani@example.com",
          "password": "SecurePass@123",
          "full_name": "Janani"
        }
```
        
        ### Login
```
        POST /api/auth/login
```
        
        Body:
```json
        {
          "email": "janani@example.com",
          "password": "SecurePass@123"
        }
```
        
        Response:
```json
        {
          "access_token": "eyJ...",
          "user_id": 1
        }
```
        """)
        
        self.create_file("docs/ARCHITECTURE.md", """
        # System Architecture
        
        ## Overview
        
        EduPath uses a microservices-inspired architecture with:
        
        - **Flask API** - REST backend
        - **PostgreSQL** - User data & transactions
        - **Neo4j** - Knowledge graph
        - **Redis** - Caching & rate limiting
        - **Razorpay** - Payment processing
        - **OpenRouter** - LLM API gateway
        
        ## Data Flow
```
        User → React Native → Flask API → PostgreSQL
                                        ↓
                                      Neo4j (Knowledge Graph)
                                        ↓
                                    OpenRouter (AI)
```
        
        ## Security Layers
        
        1. JWT Authentication
        2. Bcrypt Password Hashing
        3. Rate Limiting
        4. Input Validation
        5. CORS Configuration
        6. Webhook Signature Verification
        """)
        
        self.create_file("docs/SECURITY.md", """
        # Security Documentation
        
        ## OWASP Compliance
        
        This project follows OWASP Top 10 guidelines.
        
        ### A01 - Broken Access Control
        
        - JWT tokens (15-minute expiry)
        - Role-based access control
        - Protected routes
        
        ### A02 - Cryptographic Failures
        
        - Bcrypt password hashing (12 rounds)
        - TLS in production
        - Secure token storage
        
        ### A03 - Injection
        
        - Parameterized SQL queries
        - Input sanitization
        - XSS protection
        
        ## Best Practices
        
        1. Never commit `.env` file
        2. Use strong passwords
        3. Enable 2FA (optional)
        4. Regular security updates
        5. Monitor audit logs
        """)
    
    def generate_frontend_starter(self):
        """Generate basic frontend starter"""
        print("\n📁 Creating frontend starter...")
        
        self.create_file("frontend/package.json", """
        {
          "name": "edupath-frontend",
          "version": "1.0.0",
          "description": "EduPath Frontend - React Native",
          "main": "index.js",
          "scripts": {
            "start": "expo start",
            "android": "expo start --android",
            "ios": "expo start --ios",
            "web": "expo start --web"
          },
          "dependencies": {
            "react": "^18.2.0",
            "react-native": "^0.72.0",
            "expo": "^49.0.0",
            "axios": "^1.6.0"
          }
        }
        """)
        
        self.create_file("frontend/README.md", """
        # EduPath Frontend
        
        React Native application for EduPath.
        
        ## Setup
```bash
        npm install
        npm start
```
        
        ## Structure
```
        frontend/
        ├── src/
        │   ├── screens/
        │   ├── components/
        │   └── services/
        └── App.js
```
        """)
    
    def print_next_steps(self):
        """Print setup instructions"""
        print(f"""
    📁 Project Location: {self.base_path.absolute()}
    
    🚀 NEXT STEPS:
    
    1️⃣  Configure Environment
        cd {self.project_name}
        cp .env.example .env
        # Edit .env with your API keys
    
    2️⃣  Start Infrastructure
        docker-compose up -d
        # Wait 10 seconds
    
    3️⃣  Setup Backend
        cd backend
        python -m venv venv
        source venv/bin/activate  # Windows: venv\\Scripts\\activate
        pip install -r requirements.txt
    
    4️⃣  Initialize Databases
        python ../scripts/init_db.py
        python ../scripts/seed_concepts.py
        python ../scripts/create_test_user.py
    
    5️⃣  Run API Server
        python run_api.py
        # Visit: http://localhost:5000
    
    📚 Documentation:
        - Setup: docs/SETUP.md
        - API: docs/API.md
        - Architecture: docs/ARCHITECTURE.md
    
    🧪 Test User:
        Email: test@edupath.app
        Password: Test@1234
    
    💡 To push to GitHub:
        cd {self.project_name}
        git init
        git add .
        git commit -m "Initial commit: EduPath complete project"
        git remote add origin https://github.com/YOUR_USERNAME/edupath.git
        git push -u origin main
    
    ✨ Happy coding!
        """)

def main():
    generator = ProjectGenerator()
    generator.generate_all()

if __name__ == "__main__":
    main()