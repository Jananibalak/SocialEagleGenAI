from flask import Blueprint, request, jsonify
import json 
from backend.auth.jwt_handler import require_auth
from backend.services.ai_coach_advanced import AdvancedAICoach
from backend.payments.token_manager import TokenManager
from backend.services.neo4j_knowledge_graph import Neo4jKnowledgeGraph
from backend.services.web_search_service import WebSearchService
from shared.database import SessionLocal
from backend.models.learning_mentor import MentorMessage, LearningMentor

chat_bp = Blueprint('chat', __name__)
coach = AdvancedAICoach()
kg = Neo4jKnowledgeGraph()
web_search = WebSearchService()

@chat_bp.route('/chat', methods=['POST'])
@require_auth
def chat():
    """
    Hybrid RAG with conversation history: Neo4j + Web Search + Context
    """
    try:
        data = request.json
        message = data.get('message')
        mentor_id = data.get('mentor_id')
        conversation_history = data.get('conversation_history', [])  # ✅ NEW: Get history
        
        if not message:
            return jsonify({"error": "Message required"}), 400
        
        if not mentor_id:
            return jsonify({"error": "mentor_id required"}), 400
        
        db = SessionLocal()
        
        try:
            # Check tokens
            has_tokens, cost = TokenManager.has_sufficient_tokens(
                db, request.user_id, "chat_message"
            )
            
            if not has_tokens:
                return jsonify({"error": "Insufficient tokens"}), 402
            
            # Query Neo4j Knowledge Graph
            print(f"🔍 Querying Neo4j knowledge graph for mentor {mentor_id}")
            kg_results = kg.query_knowledge_graph(
                mentor_id=mentor_id,
                query=message,
                top_k=3
            )
            
            # Check if we need web search
            use_web_search = False
            if not kg_results:
                print("⚠️ No results from knowledge graph, will use web search")
                use_web_search = True
            elif all(r.get('relevance_score', 0) < 2 for r in kg_results):
                print("⚠️ Low relevance scores, will supplement with web search")
                use_web_search = True
            
            # Build context from knowledge graph
            kg_context = ""
            if kg_results:
                kg_context = "\n\n".join([
                    f"[From your materials: {r['source']}]\n{r['text']}"
                    for r in kg_results
                ])
            
            # Web search fallback if needed
            web_context = ""
            web_sources = []
            if use_web_search:
                print(f"🌐 Searching web for additional context")
                web_results = web_search.search(message, num_results=3)
                
                if web_results:
                    web_context = "\n\n".join([
                        f"[Web: {r['title']}]\n{r['snippet']}"
                        for r in web_results
                    ])
                    web_sources = [r['title'] for r in web_results]
            
            # Combine contexts
            combined_context = ""
            
            if kg_context:
                combined_context += "=== FROM YOUR UPLOADED MATERIALS ===\n" + kg_context
            
            if web_context:
                if combined_context:
                    combined_context += "\n\n"
                combined_context += "=== FROM WEB SEARCH ===\n" + web_context
            
            if not combined_context:
                combined_context = "(No relevant context found in materials or web)"
            
            # Get mentor info with learning plan
            mentor = db.query(LearningMentor).filter(
                LearningMentor.id == mentor_id
            ).first()
            
            if not mentor:
                return jsonify({"error": "Mentor not found"}), 404
            
            # Parse learning plan
            learning_plan = {}
            if mentor.learning_plan:
                try:
                    learning_plan = json.loads(mentor.learning_plan)
                except:
                    learning_plan = {}
            
            # ✅ NEW: Format conversation history for AI
            formatted_history = []
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                role = "user" if msg.get('sender') == 'user' else "assistant"
                formatted_history.append({
                    "role": role,
                    "content": msg.get('text', '')
                })
            
            print(f"💬 Including {len(formatted_history)} previous messages for context")
            
            # ✅ Generate AI response with conversation history
            response_text = coach.chat_with_plan_and_history(
                user_message=message,
                context=combined_context,
                mentor_info={
                    'name': mentor.name,
                    'topic': mentor.topic,
                    'personality': mentor.personality,
                },
                learning_plan=learning_plan,
                current_day=mentor.current_day or 1,
                conversation_history=formatted_history  # ✅ NEW: Pass history
            )
            
            # Save messages
            user_msg = MentorMessage(
                mentor_id=mentor_id,
                sender='user',
                message_text=message,
                tokens_used=0
            )
            db.add(user_msg)
            
            ai_msg = MentorMessage(
                mentor_id=mentor_id,
                sender='ai',
                message_text=response_text,
                tokens_used=cost
            )
            db.add(ai_msg)
            
            # Update mentor
            mentor.last_ai_message = response_text[:200]
            mentor.total_messages += 2
            
            db.commit()
            
            # Deduct tokens
            TokenManager.deduct_tokens(
                db, request.user_id, "chat_message", "Chat with mentor"
            )
            
            return jsonify({
                "response": response_text,
                "sources": {
                    "knowledge_graph": [r['source'] for r in kg_results],
                    "web_search": web_sources
                },
                "context_type": "hybrid" if (kg_results and web_sources) else ("local" if kg_results else "web")
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@chat_bp.route('/history/<int:mentor_id>', methods=['GET'])
@require_auth
def get_chat_history(mentor_id):
    """Get chat history for a specific mentor"""
    try:
        db = SessionLocal()
        
        # Verify mentor belongs to user
        mentor = db.query(LearningMentor).filter(
            LearningMentor.id == mentor_id,
            LearningMentor.user_id == request.user_id
        ).first()
        
        if not mentor:
            return jsonify({"error": "Mentor not found"}), 404
        
        # Get messages
        messages = db.query(MentorMessage).filter(
            MentorMessage.mentor_id == mentor_id
        ).order_by(MentorMessage.timestamp.asc()).all()
        
        # Format messages
        formatted_messages = [
            {
                'id': msg.id,
                'text': msg.message_text,
                'sender': msg.sender,
                'timestamp': msg.timestamp.isoformat(),
                'tokens_used': msg.tokens_used
            }
            for msg in messages
        ]
        
        print(f"✅ Fetched {len(formatted_messages)} messages for mentor {mentor_id}")
        
        return jsonify({
            'messages': formatted_messages,
            'total': len(formatted_messages)
        })
        
    except Exception as e:
        print(f"❌ Error fetching chat history: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()