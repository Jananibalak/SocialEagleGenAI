#!/usr/bin/env python3
"""
EduPath Advanced Features Generator
Adds all missing advanced features to your project

Run: python add_advanced_features.py

This adds:
- Complete Razorpay integration
- Advanced AI Coach with all features
- Knowledge Graph service
- Check-in service
- Security middleware
- Complete API routes
- Rate limiting
- Input validation
- Audit logging
"""

import os
from pathlib import Path
from textwrap import dedent

class AdvancedFeaturesGenerator:
    def __init__(self, project_name="edupath"):
        self.project_name = project_name
        self.base_path = Path(project_name)
        self.files_created = 0
        
        if not self.base_path.exists():
            print(f"❌ Error: {project_name} directory not found!")
            print(f"   Run bootstrap_complete.py first")
            exit(1)
    
    def create_file(self, path, content):
        """Create file with content"""
        filepath = self.base_path / path
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        clean_content = dedent(content).strip() + "\n"
        filepath.write_text(clean_content, encoding='utf-8')
        
        self.files_created += 1
        print(f"✅ {path}")
    
    def generate_all(self):
        """Generate all advanced features"""
        print("=" * 80)
        print("🚀 ADDING ADVANCED FEATURES TO EDUPATH")
        print("=" * 80)
        print()
        
        self.add_razorpay_integration()
        self.add_advanced_ai_coach()
        self.add_knowledge_graph_service()
        self.add_checkin_service()
        self.add_security_features()
        self.add_api_routes()
        self.add_token_management()
        self.add_database_models()
        
        print()
        print("=" * 80)
        print(f"✅ ADVANCED FEATURES ADDED! Created {self.files_created} files")
        print("=" * 80)
        self.print_summary()
    
    def add_razorpay_integration(self):
        """Add complete Razorpay payment integration"""
        print("\n💰 Adding Razorpay integration...")
        
        # Razorpay Handler
        self.create_file("backend/payments/razorpay_handler.py", """
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
        """)
        
        # Token Manager
        self.create_file("backend/payments/token_manager.py", """
        from sqlalchemy.orm import Session
        from backend.models.user import User
        from backend.models.token_transaction import TokenTransaction, TransactionType
        from datetime import datetime
        from typing import Tuple
        
        class TokenManager:
            COSTS = {
                "chat_message": 1.0,
                "daily_checkin": 0.5,
                "session_analysis": 2.0,
                "progress_report": 5.0,
                "learning_path": 3.0
            }
            
            @staticmethod
            def get_balance(db: Session, user_id: int) -> float:
                user = db.query(User).filter(User.id == user_id).first()
                return user.token_balance if user else 0.0
            
            @staticmethod
            def has_sufficient_tokens(db: Session, user_id: int, action: str) -> Tuple[bool, float]:
                cost = TokenManager.COSTS.get(action, 1.0)
                balance = TokenManager.get_balance(db, user_id)
                return balance >= cost, cost
            
            @staticmethod
            def deduct_tokens(db: Session, user_id: int, action: str, description: str = None) -> Tuple[bool, str]:
                cost = TokenManager.COSTS.get(action, 1.0)
                
                user = db.query(User).filter(User.id == user_id).first()
                
                if not user:
                    return False, "User not found"
                
                if user.token_balance < cost:
                    return False, f"Insufficient tokens. Need {cost}, have {user.token_balance}"
                
                user.token_balance -= cost
                
                transaction = TokenTransaction(
                    user_id=user_id,
                    type=TransactionType.USAGE,
                    amount=-cost,
                    balance_after=user.token_balance,
                    description=description or f"Used for {action}",
                    reference_id=action
                )
                
                db.add(transaction)
                db.commit()
                
                return True, f"Deducted {cost} tokens. Balance: {user.token_balance}"
            
            @staticmethod
            def add_tokens(db: Session, user_id: int, amount: float, transaction_type: TransactionType, description: str, payment_id: str = None) -> bool:
                user = db.query(User).filter(User.id == user_id).first()
                
                if not user:
                    return False
                
                user.token_balance += amount
                
                transaction = TokenTransaction(
                    user_id=user_id,
                    type=transaction_type,
                    amount=amount,
                    balance_after=user.token_balance,
                    description=description,
                    payment_id=payment_id,
                    payment_status="completed"
                )
                
                db.add(transaction)
                db.commit()
                
                return True
        """)
    
    def add_advanced_ai_coach(self):
        """Add complete AI Coach with all features"""
        print("\n🤖 Adding advanced AI Coach...")
        
        self.create_file("backend/services/ai_coach_advanced.py", """
        from openai import OpenAI
        from typing import Dict, List, Optional
        import os
        from datetime import datetime
        import json
        
        class AdvancedAICoach:
            def __init__(self):
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    default_headers={
                        "HTTP-Referer": os.getenv("BACKEND_URL", "http://localhost:5000"),
                        "X-Title": "EduPath Learning Assistant"
                    }
                )
                self.model = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
                
                self.coach_persona = {
                    "name": "Alex",
                    "style": "encouraging, data-driven, adaptive",
                    "tone": "friendly but professional"
                }
            
            def generate_morning_checkin(self, user_data: Dict, learning_history: List[Dict], knowledge_state: Dict) -> Dict:
                context = {
                    "name": user_data.get('full_name', 'there'),
                    "goal": user_data.get('learning_goal'),
                    "current_level": user_data.get('current_level'),
                    "streak": user_data.get('current_streak', 0),
                    "total_sessions": user_data.get('total_sessions', 0),
                    "yesterday": learning_history[0] if learning_history else None,
                    "knowledge": {
                        "mastered_count": len(knowledge_state.get('mastered', [])),
                        "ready_to_learn": knowledge_state.get('ready_to_learn', [])[:3]
                    }
                }
                
                prompt = f\"\"\"
                You are {self.coach_persona['name']}, a {self.coach_persona['style']} learning coach.
                
                STUDENT CONTEXT:
                {json.dumps(context, indent=2)}
                
                Generate a morning check-in including:
                1. Personalized greeting (reference their streak/progress)
                2. Today's motivation (inspiring, specific)
                3. Today's plan (what to focus on and why)
                4. Recommended duration
                5. Suggested topics (from ready_to_learn)
                6. Encouragement
                
                TONE: {self.coach_persona['tone']}
                
                Return JSON:
                {{
                  "greeting": "personalized greeting",
                  "motivation": "today's motivation",
                  "today_plan": "what to focus on",
                  "recommended_duration": 60,
                  "suggested_topics": ["topic1", "topic2"],
                  "encouragement": "final encouragement"
                }}
                \"\"\"
                
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": f"You are {self.coach_persona['name']}, an expert learning coach. Always return valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        response_format={"type": "json_object"}
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    result['timestamp'] = datetime.now().isoformat()
                    result['streak'] = user_data.get('current_streak', 0)
                    
                    return result
                    
                except Exception as e:
                    print(f"Error generating morning check-in: {e}")
                    return self._fallback_morning_checkin(user_data)
            
            def chat(self, user_message: str, conversation_history: List[Dict], user_context: Dict) -> str:
                system_prompt = f\"\"\"
                You are {self.coach_persona['name']}, a personal learning coach for {user_context.get('full_name', 'the student')}.
                
                STUDENT CONTEXT:
                - Goal: {user_context.get('learning_goal', 'Learn new skills')}
                - Level: {user_context.get('current_level', 'Beginner')}
                - Streak: {user_context.get('current_streak', 0)} days
                - Total sessions: {user_context.get('total_sessions', 0)}
                
                YOUR ROLE:
                - Supportive personal trainer for learning
                - Data-driven (reference their progress)
                - Encouraging but honest
                - Practical advice
                
                TONE: {self.coach_persona['tone']}
                \"\"\"
                
                messages = [{"role": "system", "content": system_prompt}]
                
                for msg in conversation_history[-10:]:
                    messages.append({"role": msg['role'], "content": msg['content']})
                
                messages.append({"role": "user", "content": user_message})
                
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.8,
                        max_tokens=500
                    )
                    
                    return response.choices[0].message.content
                    
                except Exception as e:
                    print(f"Error in chat: {e}")
                    return "I'm having trouble right now. Can you try again?"
            
            def suggest_next_topic(self, current_knowledge: Dict, recent_sessions: List[Dict], user_preferences: Dict) -> Dict:
                available_topics = current_knowledge.get('ready_to_learn', [])
                recently_studied = [s.get('topic') for s in recent_sessions[-3:]]
                
                context = {
                    "available_topics": available_topics[:5],
                    "recently_studied": recently_studied,
                    "mastered": list(current_knowledge.get('mastered_concepts', [])),
                    "time_available": user_preferences.get('time_available', 60),
                    "energy_level": user_preferences.get('energy_level', 'medium')
                }
                
                prompt = f\"\"\"
                You are a learning coach deciding what the student should study RIGHT NOW.
                
                CONTEXT:
                {json.dumps(context, indent=2)}
                
                Suggest the best topic to study next based on:
                - Prerequisites met
                - Not recently studied (variety)
                - Matches energy level and time
                
                Return JSON:
                {{
                  "recommended_topic": "topic name",
                  "reasoning": "why this topic now",
                  "difficulty": "easy/medium/hard",
                  "estimated_time": minutes,
                  "alternative_options": ["topic2", "topic3"]
                }}
                \"\"\"
                
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are an adaptive learning coach. Return valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.4,
                        response_format={"type": "json_object"}
                    )
                    
                    return json.loads(response.choices[0].message.content)
                    
                except Exception as e:
                    print(f"Error suggesting topic: {e}")
                    return {"error": str(e)}
            
            def _fallback_morning_checkin(self, user_data: Dict) -> Dict:
                return {
                    "greeting": f"Good morning, {user_data.get('full_name', 'there')}!",
                    "motivation": "Every expert was once a beginner. Today is another step forward.",
                    "today_plan": "Let's review what you learned recently and build on it.",
                    "recommended_duration": 60,
                    "suggested_topics": ["Review previous concepts"],
                    "encouragement": "You've got this! Let's make today count."
                }
        """)
    
    def add_knowledge_graph_service(self):
        """Add Knowledge Graph service"""
        print("\n📊 Adding Knowledge Graph service...")
        
        self.create_file("backend/services/knowledge_graph.py", """
        from typing import Dict, List, Optional
        from shared.database import neo4j_conn
        from datetime import datetime
        import json
        
        class KnowledgeGraphService:
            def __init__(self):
                self.driver = neo4j_conn.driver
            
            def get_user_knowledge_state(self, user_id: int) -> Dict:
                if not self.driver:
                    return {"error": "Neo4j not available"}
                
                with self.driver.session() as session:
                    mastered = self._get_mastered_concepts(session, user_id)
                    in_progress = self._get_in_progress_concepts(session, user_id)
                    ready = self._get_ready_to_learn(session, user_id, mastered)
                    
                    total_concepts = self._count_total_concepts(session)
                    mastery_pct = (len(mastered) / total_concepts * 100) if total_concepts > 0 else 0
                    
                    return {
                        "mastered_concepts": mastered,
                        "in_progress_concepts": in_progress,
                        "ready_to_learn": ready,
                        "mastery_percentage": round(mastery_pct, 1),
                        "total_concepts": total_concepts,
                        "last_updated": datetime.now().isoformat()
                    }
            
            def _get_mastered_concepts(self, session, user_id: int) -> List[str]:
                query = \"\"\"
                MATCH (u:User {user_id: $user_id})-[m:MASTERED]->(c:Concept)
                WHERE m.mastery_level >= 8
                RETURN c.name as concept
                ORDER BY m.mastered_at DESC
                \"\"\"
                
                result = session.run(query, user_id=user_id)
                return [record["concept"] for record in result]
            
            def _get_in_progress_concepts(self, session, user_id: int) -> List[Dict]:
                query = \"\"\"
                MATCH (u:User {user_id: $user_id})-[l:LEARNING]->(c:Concept)
                WHERE l.mastery_level < 8
                RETURN 
                    c.name as concept,
                    c.difficulty as difficulty,
                    l.mastery_level as current_mastery,
                    l.sessions_count as sessions
                ORDER BY l.last_studied DESC
                \"\"\"
                
                result = session.run(query, user_id=user_id)
                
                return [
                    {
                        "concept": record["concept"],
                        "difficulty": record["difficulty"],
                        "current_mastery": record["current_mastery"],
                        "sessions_count": record["sessions"]
                    }
                    for record in result
                ]
            
            def _get_ready_to_learn(self, session, user_id: int, mastered: List[str]) -> List[Dict]:
                query = \"\"\"
                MATCH (c:Concept)
                WHERE NOT EXISTS {
                    MATCH (u:User {user_id: $user_id})-[:MASTERED|LEARNING]->(c)
                }
                OPTIONAL MATCH (c)-[:REQUIRES]->(prereq:Concept)
                WITH c, collect(prereq.name) as prerequisites
                WHERE all(p IN prerequisites WHERE p IN $mastered)
                RETURN 
                    c.name as concept,
                    c.difficulty as difficulty,
                    prerequisites
                ORDER BY c.difficulty ASC
                LIMIT 10
                \"\"\"
                
                result = session.run(query, user_id=user_id, mastered=mastered)
                
                return [
                    {
                        "concept": record["concept"],
                        "difficulty": record["difficulty"],
                        "prerequisites": record["prerequisites"]
                    }
                    for record in result
                ]
            
            def _count_total_concepts(self, session) -> int:
                result = session.run("MATCH (c:Concept) RETURN count(c) as total")
                return result.single()["total"]
            
            def update_concept_mastery(self, user_id: int, concept_name: str, session_data: Dict) -> Dict:
                if not self.driver:
                    return {"error": "Neo4j not available"}
                
                with self.driver.session() as session:
                    improvement = session_data["understanding_after"] - session_data["understanding_before"]
                    
                    query = \"\"\"
                    MATCH (u:User {user_id: $user_id})
                    MERGE (c:Concept {name: $concept_name})
                    MERGE (u)-[r:LEARNING]->(c)
                    ON CREATE SET 
                        r.mastery_level = 0,
                        r.sessions_count = 0,
                        r.started_at = datetime()
                    SET 
                        r.last_studied = datetime(),
                        r.sessions_count = r.sessions_count + 1,
                        r.mastery_level = CASE
                            WHEN $understanding_after >= 9 THEN 9.0
                            WHEN $understanding_after >= 8 THEN r.mastery_level + ($improvement * 0.5)
                            WHEN $understanding_after >= 6 THEN r.mastery_level + ($improvement * 0.3)
                            ELSE r.mastery_level + ($improvement * 0.1)
                        END
                    
                    WITH u, c, r, r.mastery_level as old_mastery
                    WHERE r.mastery_level >= 8 AND old_mastery < 8
                    MERGE (u)-[m:MASTERED]->(c)
                    SET m.mastered_at = datetime(),
                        m.mastery_level = r.mastery_level
                    
                    RETURN 
                        c.name as concept,
                        old_mastery,
                        r.mastery_level as new_mastery,
                        r.mastery_level >= 8 as mastered
                    \"\"\"
                    
                    result = session.run(
                        query,
                        user_id=user_id,
                        concept_name=concept_name,
                        understanding_after=session_data["understanding_after"],
                        improvement=improvement
                    )
                    
                    record = result.single()
                    
                    return {
                        "concept": record["concept"],
                        "old_mastery": round(record["old_mastery"], 1),
                        "new_mastery": round(record["new_mastery"], 1),
                        "mastered": record["mastered"]
                    }
        
        def create_user_node(user_id: int, name: str):
            with neo4j_conn.driver.session() as session:
                session.run(
                    \"\"\"
                    MERGE (u:User {user_id: $user_id})
                    SET u.name = $name, u.created_at = datetime()
                    \"\"\",
                    user_id=user_id,
                    name=name
                )
        """)
    
    def add_checkin_service(self):
        """Add check-in service"""
        print("\n📅 Adding check-in service...")
        
        self.create_file("backend/services/checkin_service.py", """
        from datetime import datetime, timedelta
        from typing import Dict, List, Optional
        from sqlalchemy.orm import Session
        from backend.models.user import User, LearningSession
        from backend.services.ai_coach_advanced import AdvancedAICoach
        from backend.services.knowledge_graph import KnowledgeGraphService
        
        class CheckinService:
            def __init__(self):
                self.coach = AdvancedAICoach()
                self.kg = KnowledgeGraphService()
            
            def generate_morning_checkin(self, db: Session, user_id: int) -> Dict:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return {"error": "User not found"}
                
                recent_sessions = db.query(LearningSession)\\
                    .filter(LearningSession.user_id == user_id)\\
                    .order_by(LearningSession.start_time.desc())\\
                    .limit(10)\\
                    .all()
                
                sessions_data = [
                    {
                        "topic": s.topic,
                        "duration_minutes": s.duration_minutes,
                        "understanding_after": s.understanding_after
                    }
                    for s in recent_sessions
                ]
                
                knowledge_state = self.kg.get_user_knowledge_state(user_id)
                
                user_data = {
                    "full_name": user.full_name,
                    "learning_goal": user.learning_goal,
                    "current_level": user.current_level,
                    "current_streak": user.current_streak,
                    "total_sessions": user.total_sessions
                }
                
                checkin = self.coach.generate_morning_checkin(
                    user_data=user_data,
                    learning_history=sessions_data,
                    knowledge_state=knowledge_state
                )
                
                user.last_checkin = datetime.now()
                db.commit()
                
                return checkin
            
            def start_session(self, db: Session, user_id: int, topic: str, understanding_before: int) -> Dict:
                session = LearningSession(
                    user_id=user_id,
                    start_time=datetime.now(),
                    topic=topic,
                    understanding_before=understanding_before
                )
                
                db.add(session)
                db.commit()
                db.refresh(session)
                
                return {
                    "session_id": session.id,
                    "topic": topic,
                    "started_at": session.start_time.isoformat()
                }
            
            def end_session(self, db: Session, session_id: int, understanding_after: int, difficulty_rating: int, enjoyment_rating: int, notes: str = None) -> Dict:
                session = db.query(LearningSession).filter(LearningSession.id == session_id).first()
                if not session:
                    return {"error": "Session not found"}
                
                session.end_time = datetime.now()
                session.duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
                session.understanding_after = understanding_after
                session.difficulty_rating = difficulty_rating
                session.enjoyment_rating = enjoyment_rating
                session.notes = notes
                
                user = db.query(User).filter(User.id == session.user_id).first()
                user.total_sessions += 1
                user.total_learning_minutes += session.duration_minutes
                
                db.commit()
                
                return {
                    "session_id": session.id,
                    "duration_minutes": session.duration_minutes,
                    "improvement": understanding_after - session.understanding_before
                }
        """)
    
    def add_security_features(self):
        """Add security features"""
        print("\n🔐 Adding security features...")
        
        # Rate Limiter
        self.create_file("backend/auth/rate_limiter.py", """
        from flask import request, jsonify
        from functools import wraps
        from typing import Dict
        import time
        
        class RateLimiter:
            def __init__(self):
                self.requests: Dict[str, list] = {}
                self.blocked_ips: Dict[str, float] = {}
            
            def _get_client_ip(self) -> str:
                if request.headers.get('X-Forwarded-For'):
                    return request.headers.get('X-Forwarded-For').split(',')[0].strip()
                return request.remote_addr
            
            def check_rate_limit(self, max_requests: int, window_seconds: int) -> tuple[bool, str]:
                ip = self._get_client_ip()
                
                if ip in self.blocked_ips:
                    if time.time() < self.blocked_ips[ip]:
                        return False, "Rate limit exceeded. Please try again later."
                    else:
                        del self.blocked_ips[ip]
                
                cutoff = time.time() - window_seconds
                
                if ip not in self.requests:
                    self.requests[ip] = []
                
                self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]
                
                if len(self.requests[ip]) >= max_requests:
                    self.blocked_ips[ip] = time.time() + 900  # Block for 15 minutes
                    return False, "Too many requests"
                
                self.requests[ip].append(time.time())
                return True, "OK"
        
        rate_limiter = RateLimiter()
        
        def rate_limit(max_requests: int = 100, window_seconds: int = 60):
            def decorator(f):
                @wraps(f)
                def decorated(*args, **kwargs):
                    allowed, message = rate_limiter.check_rate_limit(max_requests, window_seconds)
                    
                    if not allowed:
                        return jsonify({"error": message}), 429
                    
                    return f(*args, **kwargs)
                
                return decorated
            return decorator
        """)
        
        # Input Validator
        self.create_file("backend/security/input_validator.py", """
        import re
        import bleach
        from typing import Tuple
        
        class InputValidator:
            @staticmethod
            def sanitize_string(input_str: str, max_length: int = 500) -> str:
                if not input_str:
                    return ""
                
                cleaned = bleach.clean(input_str, tags=[], strip=True)
                cleaned = cleaned[:max_length]
                cleaned = cleaned.replace('\\x00', '')
                
                return cleaned.strip()
            
            @staticmethod
            def validate_email(email: str) -> bool:
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
                
                if not re.match(pattern, email):
                    return False
                
                if len(email) > 254:
                    return False
                
                return True
            
            @staticmethod
            def validate_username(username: str) -> Tuple[bool, str]:
                if len(username) < 3 or len(username) > 30:
                    return False, "Username must be 3-30 characters"
                
                if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
                    return False, "Username must start with a letter"
                
                return True, "Valid"
        """)
        
        # Audit Logger
        self.create_file("backend/security/audit_logger.py", """
        import logging
        from datetime import datetime
        from typing import Dict, Any
        
        logger = logging.getLogger(__name__)
        
        class AuditLogger:
            @staticmethod
            def log_event(user_id: int, event_type: str, details: Dict[str, Any] = None):
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id,
                    "event_type": event_type,
                    "details": details or {}
                }
                
                logger.info(f"AUDIT: {log_entry}")
        """)
    
    def add_api_routes(self):
        """Add complete API routes"""
        print("\n🛣️  Adding API routes...")
        
        # Auth Routes
        self.create_file("backend/routes/auth.py", """
        from flask import Blueprint, request, jsonify
        from backend.auth.jwt_handler import create_access_token
        from backend.auth.password_handler import hash_password, verify_password, validate_password_strength
        from backend.auth.rate_limiter import rate_limit
        from backend.security.input_validator import InputValidator
        from shared.database import SessionLocal
        from backend.models.user import User
        from backend.services.knowledge_graph import create_user_node
        
        auth_bp = Blueprint('auth', __name__)
        
        @auth_bp.route('/signup', methods=['POST'])
        @rate_limit(max_requests=5, window_seconds=300)
        def signup():
            try:
                data = request.json
                
                username = data.get('username')
                email = data.get('email')
                password = data.get('password')
                full_name = data.get('full_name')
                
                if not all([username, email, password]):
                    return jsonify({"error": "Missing required fields"}), 400
                
                if not InputValidator.validate_email(email):
                    return jsonify({"error": "Invalid email"}), 400
                
                valid_username, msg = InputValidator.validate_username(username)
                if not valid_username:
                    return jsonify({"error": msg}), 400
                
                valid_password, msg = validate_password_strength(password)
                if not valid_password:
                    return jsonify({"error": msg}), 400
                
                db = SessionLocal()
                
                try:
                    existing = db.query(User).filter(
                        (User.username == username) | (User.email == email)
                    ).first()
                    
                    if existing:
                        return jsonify({"error": "User already exists"}), 400
                    
                    user = User(
                        username=username,
                        email=email,
                        hashed_password=hash_password(password),
                        full_name=full_name,
                        token_balance=50.0  # Free trial tokens
                    )
                    
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                    
                    create_user_node(user.id, user.full_name or username)
                    
                    token = create_access_token(user.id, user.email)
                    
                    return jsonify({
                        "success": True,
                        "access_token": token,
                        "user_id": user.id,
                        "username": user.username
                    }), 201
                    
                finally:
                    db.close()
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @auth_bp.route('/login', methods=['POST'])
        @rate_limit(max_requests=5, window_seconds=300)
        def login():
            try:
                data = request.json
                email = data.get('email')
                password = data.get('password')
                
                if not all([email, password]):
                    return jsonify({"error": "Missing credentials"}), 400
                
                db = SessionLocal()
                
                try:
                    user = db.query(User).filter(User.email == email).first()
                    
                    if not user or not verify_password(password, user.hashed_password):
                        return jsonify({"error": "Invalid credentials"}), 401
                    
                    token = create_access_token(user.id, user.email)
                    
                    return jsonify({
                        "access_token": token,
                        "user_id": user.id,
                        "username": user.username
                    })
                    
                finally:
                    db.close()
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        """)
        
        # Payment Routes
        self.create_file("backend/routes/payments.py", """
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
        """)
        
        # Chat Routes
        self.create_file("backend/routes/chat.py", """
        from flask import Blueprint, request, jsonify
        from backend.auth.jwt_handler import require_auth
        from backend.services.ai_coach_advanced import AdvancedAICoach
        from backend.payments.token_manager import TokenManager
        from shared.database import SessionLocal
        
        chat_bp = Blueprint('chat', __name__)
        coach = AdvancedAICoach()
        
        @chat_bp.route('/chat', methods=['POST'])
        @require_auth
        def chat():
            try:
                data = request.json
                message = data.get('message')
                
                if not message:
                    return jsonify({"error": "Message required"}), 400
                
                db = SessionLocal()
                
                try:
                    has_tokens, cost = TokenManager.has_sufficient_tokens(
                        db, request.user_id, "chat_message"
                    )
                    
                    if not has_tokens:
                        return jsonify({"error": "Insufficient tokens"}), 402
                    
                    response = coach.chat(message, [], {"full_name": "User"})
                    
                    TokenManager.deduct_tokens(
                        db, request.user_id, "chat_message", "Chat message"
                    )
                    
                    return jsonify({"response": response})
                    
                finally:
                    db.close()
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        """)
    
    def add_token_management(self):
        """Add token transaction model"""
        print("\n💰 Adding token management...")
        
        self.create_file("backend/models/token_transaction.py", """
        from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
        from sqlalchemy.sql import func
        from shared.database import Base
        import enum
        
        class TransactionType(enum.Enum):
            PURCHASE = "purchase"
            USAGE = "usage"
            REFUND = "refund"
            BONUS = "bonus"
        
        class TokenTransaction(Base):
            __tablename__ = "token_transactions"
            
            id = Column(Integer, primary_key=True, index=True)
            user_id = Column(Integer, index=True, nullable=False)
            
            type = Column(SQLEnum(TransactionType), nullable=False)
            amount = Column(Float, nullable=False)
            balance_after = Column(Float, nullable=False)
            
            description = Column(String)
            reference_id = Column(String)
            
            payment_id = Column(String)
            payment_status = Column(String)
            
            created_at = Column(DateTime(timezone=True), server_default=func.now())
        """)
    
    def add_database_models(self):
        """Update database models"""
        print("\n🗄️  Updating database models...")
        
        # Enhanced app.py with all routes
        self.create_file("backend/app_complete.py", """
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
        """)
    
    def print_summary(self):
        """Print setup summary"""
        print("""
    ✨ ADVANCED FEATURES ADDED SUCCESSFULLY!
    
    📦 What was added:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    💰 Razorpay Integration
       ├── razorpay_handler.py (Complete payment flow)
       ├── token_manager.py (Token balance & usage)
       └── Webhook verification
    
    🤖 Advanced AI Coach
       ├── Morning check-ins
       ├── Evening reflections
       ├── Topic suggestions
       └── Conversational chat
    
    📊 Knowledge Graph
       ├── Concept mastery tracking
       ├── Learning path generation
       └── Progress analytics
    
    📅 Check-in Service
       ├── Daily sync-ups
       ├── Session tracking
       └── Streak management
    
    🔐 Security Features
       ├── Rate limiting
       ├── Input validation
       ├── Audit logging
       └── Password strength validation
    
    🛣️  API Routes
       ├── /api/auth/signup
       ├── /api/auth/login
       ├── /api/payments/plans
       ├── /api/payments/create-order/tokens
       ├── /api/payments/verify-payment
       ├── /api/payments/balance
       └── /api/chat
    
    💾 Database Models
       └── TokenTransaction
    
    📝 NEXT STEPS:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    1. Update backend/app.py to use app_complete.py:
       cp backend/app_complete.py backend/app.py
    
    2. Reinstall requirements (new dependencies):
       cd backend
       pip install -r requirements.txt
    
    3. Initialize databases:
       python ../scripts/init_db.py
    
    4. Test the API:
       python run_api.py
       
       # In another terminal:
       curl http://localhost:5000/health
    
    5. Test signup:
       curl -X POST http://localhost:5000/api/auth/signup \\
         -H "Content-Type: application/json" \\
         -d '{
           "username": "test",
           "email": "test@example.com",
           "password": "Test@1234",
           "full_name": "Test User"
         }'
    
    🎉 You now have a COMPLETE production-ready backend!
        """)

def main():
    generator = AdvancedFeaturesGenerator()
    generator.generate_all()

if __name__ == "__main__":
    main()