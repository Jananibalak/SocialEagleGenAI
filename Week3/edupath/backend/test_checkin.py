from datetime import datetime
from shared.database import SessionLocal, engine, Base
from models.user import User, LearningSession
from services.checkin_service import CheckinService

# Create tables
Base.metadata.create_all(bind=engine)

print("="*70)
print("TESTING CHECK-IN SERVICE")
print("="*70)

# Create test database session
db = SessionLocal()

try:
    # Create test user
    test_user = User(
        username="janani_test",
        email="janani@test.com",
        hashed_password="hashed",
        full_name="Janani",
        learning_goal="Learn Machine Learning",
        current_level="Beginner",
        current_streak=5,
        total_sessions=12,
        total_learning_minutes=720
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    print(f"\n✓ Created test user: {test_user.full_name} (ID: {test_user.id})")
    
    # Initialize service
    checkin_service = CheckinService()
    
    # Test 1: Morning check-in
    print("\n[Test 1] Morning Check-in")
    print("-"*70)
    morning = checkin_service.generate_morning_checkin(db, test_user.id)
    print(f"Greeting: {morning.get('greeting', 'N/A')}")
    print(f"Today's Plan: {morning.get('today_plan', 'N/A')[:100]}...")
    print(f"Streak: {morning.get('streak_info', {})}")
    
    # Test 2: Start session
    print("\n[Test 2] Start Learning Session")
    print("-"*70)
    session_start = checkin_service.start_session(
        db=db,
        user_id=test_user.id,
        topic="Linear Algebra",
        understanding_before=4
    )
    print(f"Session ID: {session_start.get('session_id')}")
    print(f"Started at: {session_start.get('started_at')}")
    
    # Test 3: End session
    print("\n[Test 3] End Learning Session")
    print("-"*70)
    session_end = checkin_service.end_session(
        db=db,
        session_id=session_start['session_id'],
        understanding_after=8,
        difficulty_rating=6,
        enjoyment_rating=7,
        notes="Great session on vectors!",
        concepts_mastered=["Vectors", "Matrix Operations"]
    )
    print(f"Duration: {session_end.get('duration_minutes')} minutes")
    print(f"Improvement: +{session_end.get('improvement')}")
    print(f"Streak: {session_end.get('streak', {}).get('current_streak')} days")
    print(f"Feedback: {session_end.get('feedback', {}).get('overall')}")
    
    # Test 4: Evening reflection
    print("\n[Test 4] Evening Reflection")
    print("-"*70)
    reflection = checkin_service.generate_evening_reflection(db, test_user.id)
    print(f"Summary: {reflection.get('summary', 'N/A')[:150]}...")
    if 'wins' in reflection:
        print(f"Wins: {len(reflection.get('wins', []))} wins identified")
    
    # Test 5: Daily summary
    print("\n[Test 5] Daily Summary")
    print("-"*70)
    summary = checkin_service.get_daily_summary(db, test_user.id)
    print(f"Date: {summary.get('date')}")
    print(f"Session completed: {summary.get('session_completed')}")
    print(f"Current streak: {summary.get('streak', {}).get('current')}")
    
    print("\n" + "="*70)
    print("✓ Check-in Service tests complete!")
    print("="*70)
    
finally:
    # Cleanup
    db.query(LearningSession).delete()
    db.query(User).delete()
    db.commit()
    db.close()