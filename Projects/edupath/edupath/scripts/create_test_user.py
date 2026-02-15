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
