from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Use absolute imports from project root
from shared.database import SessionLocal, engine, Base
from backend.models.user import User, LearningSession, Goal
from backend.services.ai_coach import AICoach
from backend.services.knowledge_graph import KnowledgeGraphService
from backend.services.checkin_service import CheckinService

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Streamlit

# Initialize services
ai_coach = AICoach()
kg_service = KnowledgeGraphService()
checkin_service = CheckinService()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# ═══════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════

@app.route('/health', methods=['GET'])
def health_check():
    """Check if API is running"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ai_coach": "initialized",
            "knowledge_graph": "initialized",
            "checkin": "initialized"
        }
    })

# ═══════════════════════════════════════════════════════════════
# USER ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/user/create', methods=['POST'])
def create_user():
    """
    Create a new user
    
    Body:
    {
        "username": "janani",
        "email": "janani@email.com",
        "full_name": "Janani",
        "learning_goal": "Learn Machine Learning",
        "current_level": "Beginner"
    }
    """
    try:
        data = request.json
        db = get_db()
        
        # Check if user exists
        existing = db.query(User).filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing:
            return jsonify({"error": "User already exists"}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            hashed_password="hashed_" + data.get('password', 'default'),  # TODO: Proper hashing
            full_name=data['full_name'],
            learning_goal=data.get('learning_goal'),
            current_level=data.get('current_level', 'Beginner'),
            daily_checkin_time=data.get('daily_checkin_time', '09:00'),
            preferred_learning_duration=data.get('preferred_learning_duration', 60)
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create user node in Neo4j
        from services.knowledge_graph import create_user_node
        create_user_node(user.id, user.full_name)
        
        return jsonify({
            "success": True,
            "user_id": user.id,
            "username": user.username,
            "message": "User created successfully!"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile and stats"""
    try:
        db = get_db()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get knowledge graph stats
        kg_stats = kg_service.get_learning_statistics(user_id)
        
        return jsonify({
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "learning_goal": user.learning_goal,
            "current_level": user.current_level,
            "stats": {
                "current_streak": user.current_streak,
                "longest_streak": user.longest_streak,
                "total_sessions": user.total_sessions,
                "total_learning_hours": round(user.total_learning_minutes / 60, 1),
                "mastery_score": user.mastery_score
            },
            "knowledge_graph": kg_stats
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# DAILY CHECK-IN ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/checkin/morning/<int:user_id>', methods=['GET'])
def morning_checkin(user_id):
    """Get personalized morning check-in"""
    try:
        db = get_db()
        checkin = checkin_service.generate_morning_checkin(db, user_id)
        return jsonify(checkin)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/checkin/evening/<int:user_id>', methods=['GET'])
def evening_reflection(user_id):
    """Get evening reflection"""
    try:
        db = get_db()
        reflection = checkin_service.generate_evening_reflection(db, user_id)
        return jsonify(reflection)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/checkin/streak/<int:user_id>', methods=['GET'])
def check_streak(user_id):
    """Check streak status"""
    try:
        db = get_db()
        streak_status = checkin_service.check_streak_at_risk(db, user_id)
        return jsonify(streak_status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# LEARNING SESSION ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/session/start', methods=['POST'])
def start_session():
    """
    Start a learning session
    
    Body:
    {
        "user_id": 1,
        "topic": "Linear Algebra",
        "understanding_before": 4
    }
    """
    try:
        data = request.json
        db = get_db()
        
        result = checkin_service.start_session(
            db=db,
            user_id=data['user_id'],
            topic=data['topic'],
            understanding_before=data['understanding_before']
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/session/end', methods=['POST'])
def end_session():
    """
    End a learning session
    
    Body:
    {
        "session_id": 1,
        "understanding_after": 8,
        "difficulty_rating": 6,
        "enjoyment_rating": 7,
        "notes": "Great session!",
        "concepts_mastered": ["Vectors", "Matrices"]
    }
    """
    try:
        data = request.json
        db = get_db()
        
        result = checkin_service.end_session(
            db=db,
            session_id=data['session_id'],
            understanding_after=data['understanding_after'],
            difficulty_rating=data['difficulty_rating'],
            enjoyment_rating=data['enjoyment_rating'],
            notes=data.get('notes'),
            concepts_mastered=data.get('concepts_mastered', [])
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<int:user_id>', methods=['GET'])
def get_user_sessions(user_id):
    """Get user's learning sessions"""
    try:
        db = get_db()
        
        # Get optional filters
        limit = request.args.get('limit', 10, type=int)
        
        sessions = db.query(LearningSession)\
            .filter(LearningSession.user_id == user_id)\
            .order_by(LearningSession.start_time.desc())\
            .limit(limit)\
            .all()
        
        return jsonify([
            {
                "id": s.id,
                "topic": s.topic,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "duration_minutes": s.duration_minutes,
                "understanding_before": s.understanding_before,
                "understanding_after": s.understanding_after,
                "improvement": s.understanding_after - s.understanding_before if s.understanding_after else 0,
                "difficulty_rating": s.difficulty_rating,
                "enjoyment_rating": s.enjoyment_rating,
                "concepts_mastered": s.concepts_mastered,
                "notes": s.notes
            }
            for s in sessions
        ])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# KNOWLEDGE GRAPH ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/knowledge/state/<int:user_id>', methods=['GET'])
def get_knowledge_state(user_id):
    """Get user's current knowledge state"""
    try:
        state = kg_service.get_user_knowledge_state(user_id)
        return jsonify(state)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/knowledge/path/<int:user_id>/<string:target_concept>', methods=['GET'])
def get_learning_path(user_id, target_concept):
    """Get learning path to target concept"""
    try:
        path = kg_service.generate_learning_path(user_id, target_concept)
        return jsonify(path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/knowledge/next/<int:user_id>', methods=['POST'])
def get_next_topic(user_id):
    """
    Get suggested next topic to study
    
    Body:
    {
        "time_available": 60,
        "energy_level": "high"
    }
    """
    try:
        data = request.json
        db = get_db()
        
        # Get knowledge state
        knowledge_state = kg_service.get_user_knowledge_state(user_id)
        
        # Get recent sessions
        recent_sessions = db.query(LearningSession)\
            .filter(LearningSession.user_id == user_id)\
            .order_by(LearningSession.start_time.desc())\
            .limit(5)\
            .all()
        
        recent_data = [
            {"topic": s.topic, "understanding_after": s.understanding_after}
            for s in recent_sessions
        ]
        
        # Get AI suggestion
        suggestion = ai_coach.suggest_next_topic(
            current_knowledge=knowledge_state,
            recent_sessions=recent_data,
            user_preferences={
                "time_available": data.get("time_available", 60),
                "energy_level": data.get("energy_level", "medium"),
                "difficulty_preference": data.get("difficulty_preference", "progressive")
            }
        )
        
        return jsonify(suggestion)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# AI COACH ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/coach/chat', methods=['POST'])
def chat_with_coach():
    """
    Chat with AI coach
    
    Body:
    {
        "user_id": 1,
        "message": "I'm struggling with linear algebra",
        "conversation_history": []
    }
    """
    try:
        data = request.json
        db = get_db()
        
        # Get user context
        user = db.query(User).filter(User.id == data['user_id']).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get recent sessions for context
        recent_sessions = db.query(LearningSession)\
            .filter(LearningSession.user_id == data['user_id'])\
            .order_by(LearningSession.start_time.desc())\
            .limit(5)\
            .all()
        
        user_context = {
            "full_name": user.full_name,
            "learning_goal": user.learning_goal,
            "current_level": user.current_level,
            "current_streak": user.current_streak,
            "total_sessions": user.total_sessions,
            "recent_topics": [s.topic for s in recent_sessions if s.topic]
        }
        
        # Get AI response
        response = ai_coach.chat(
            user_message=data['message'],
            conversation_history=data.get('conversation_history', []),
            user_context=user_context
        )
        
        return jsonify({
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/coach/analyze-patterns/<int:user_id>', methods=['GET'])
def analyze_patterns(user_id):
    """Analyze learning patterns"""
    try:
        db = get_db()
        
        # Get sessions from last 30 days
        sessions = db.query(LearningSession)\
            .filter(LearningSession.user_id == user_id)\
            .order_by(LearningSession.start_time.desc())\
            .limit(50)\
            .all()
        
        sessions_data = [
            {
                "topic": s.topic,
                "duration_minutes": s.duration_minutes,
                "understanding_before": s.understanding_before,
                "understanding_after": s.understanding_after,
                "difficulty_rating": s.difficulty_rating,
                "enjoyment_rating": s.enjoyment_rating,
                "start_time": s.start_time.isoformat() if s.start_time else None
            }
            for s in sessions
        ]
        
        analysis = ai_coach.analyze_learning_patterns(sessions_data, timeframe_days=30)
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/coach/detect-struggles/<int:user_id>', methods=['GET'])
def detect_struggles(user_id):
    """Detect if user is struggling"""
    try:
        db = get_db()
        
        # Get recent sessions
        recent_sessions = db.query(LearningSession)\
            .filter(LearningSession.user_id == user_id)\
            .order_by(LearningSession.start_time.desc())\
            .limit(10)\
            .all()
        
        sessions_data = [
            {
                "topic": s.topic,
                "understanding_before": s.understanding_before,
                "understanding_after": s.understanding_after,
                "difficulty_rating": s.difficulty_rating,
                "enjoyment_rating": s.enjoyment_rating
            }
            for s in recent_sessions
        ]
        
        # Get knowledge graph data
        knowledge_state = kg_service.get_user_knowledge_state(user_id)
        
        struggles = ai_coach.detect_struggles(
            recent_sessions=sessions_data,
            knowledge_graph_data=knowledge_state
        )
        
        return jsonify(struggles)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# DASHBOARD ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/dashboard/<int:user_id>', methods=['GET'])
def get_dashboard(user_id):
    """Get complete dashboard data"""
    try:
        db = get_db()
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get today's summary
        daily_summary = checkin_service.get_daily_summary(db, user_id)
        
        # Get knowledge state
        knowledge_state = kg_service.get_user_knowledge_state(user_id)
        
        # Get recent sessions
        recent_sessions = db.query(LearningSession)\
            .filter(LearningSession.user_id == user_id)\
            .order_by(LearningSession.start_time.desc())\
            .limit(7)\
            .all()
        
        # Calculate weekly stats
        weekly_minutes = sum(s.duration_minutes or 0 for s in recent_sessions)
        weekly_sessions = len(recent_sessions)
        
        return jsonify({
            "user": {
                "name": user.full_name,
                "goal": user.learning_goal,
                "level": user.current_level
            },
            "today": daily_summary,
            "streak": {
                "current": user.current_streak,
                "longest": user.longest_streak,
                "status": checkin_service._get_streak_status(user.current_streak)
            },
            "this_week": {
                "sessions": weekly_sessions,
                "total_minutes": weekly_minutes,
                "avg_session_length": round(weekly_minutes / weekly_sessions, 1) if weekly_sessions > 0 else 0
            },
            "knowledge": {
                "mastered": len(knowledge_state.get("mastered_concepts", [])),
                "in_progress": len(knowledge_state.get("in_progress_concepts", [])),
                "ready_to_learn": len(knowledge_state.get("ready_to_learn", [])),
                "mastery_percentage": knowledge_state.get("mastery_percentage", 0)
            },
            "recent_sessions": [
                {
                    "topic": s.topic,
                    "date": s.start_time.date().isoformat() if s.start_time else None,
                    "duration": s.duration_minutes,
                    "improvement": s.understanding_after - s.understanding_before if s.understanding_after else 0
                }
                for s in recent_sessions
            ]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# RUN SERVER
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("="*70)
    print("🚀 EDUPATH API SERVER STARTING")
    print("="*70)
    print(f"Server running at: http://localhost:5000")
    print(f"Health check: http://localhost:5000/health")
    print("="*70)
    
    app.run(host='0.0.0.0', port=5000, debug=True)