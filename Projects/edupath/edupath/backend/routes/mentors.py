from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.services.learning_plan_generator import LearningPlanGenerator
import json 

from backend.auth.jwt_handler import require_auth
from backend.models.learning_mentor import LearningMentor, KnowledgeScroll
from backend.services.document_processor import DocumentProcessor
from backend.services.ai_mentor_namer import AIMentorNamer
from backend.services.knowledge_base_manager import KnowledgeBaseManager
from shared.database import SessionLocal
 # ✅ CHANGED: Use Neo4j instead of simple JSON
from backend.services.neo4j_knowledge_graph import Neo4jKnowledgeGraph

mentors_bp = Blueprint('mentors', __name__)

# Upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'data', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@mentors_bp.route('/create-mentor', methods=['POST'])
@require_auth
def create_mentor():
    """
    Create a new mentor from uploaded document or YouTube URL
    
    Request (multipart/form-data):
        - file: Document file (PDF/DOCX/TXT) OR
        - youtube_url: YouTube video URL
        - topic: (optional) Topic override
        - target_days: (optional) Learning goal in days
    """
    try:
        db = SessionLocal()
        user_id = request.user_id
        
        # Get form data
        topic = request.form.get('topic', '')
        target_days = request.form.get('target_days', 30)
        youtube_url = request.form.get('youtube_url', '')
        
        # Process document
        if youtube_url:
            # YouTube video
            print(f"📺 Processing YouTube URL: {youtube_url}")
            
            result = DocumentProcessor.process_document(url=youtube_url)
            
            # ✅ FIX: Check if processing succeeded
            if not result['success']:
                error_msg = result.get('error', 'Failed to extract YouTube transcript')
                print(f"❌ YouTube processing failed: {error_msg}")
                
                # Return user-friendly error
                return jsonify({
                    'error': error_msg,
                    'error_type': 'youtube_transcript',
                    'suggestions': [
                        'Try a video with captions/subtitles enabled',
                        'Avoid age-restricted or private videos',
                        'Use a TED Talk or educational video',
                        'Or upload a PDF/DOCX file instead'
                    ]
                }), 400
            
            extracted_text = result['text']
            
            # ✅ Validate extracted text
            if not extracted_text or len(extracted_text) < 100:
                return jsonify({
                    'error': 'Transcript too short or empty. Video may not have proper captions.',
                    'error_type': 'youtube_transcript',
                    'suggestions': [
                        'Choose a longer video (at least 5 minutes)',
                        'Verify the video has captions enabled',
                        'Try uploading a document instead'
                    ]
                }), 400
            
            file_name = result.get('metadata', {}).get('title', 'YouTube Video')
            file_type = 'youtube'
            file_url = youtube_url
            file_size = len(extracted_text)
            
            print(f"✅ YouTube transcript extracted: {len(extracted_text)} characters")
            
        elif 'file' in request.files:
            # Uploaded file
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed. Use PDF, DOCX, or TXT'}), 400
            
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            print(f"📄 Processing file: {filename}")
            
            # Process file
            result = DocumentProcessor.process_document(file_path=file_path)
            
            # ✅ Check if processing succeeded
            if not result['success']:
                error_msg = result.get('error', 'Failed to process document')
                print(f"❌ File processing failed: {error_msg}")
                return jsonify({'error': error_msg}), 400
            
            extracted_text = result['text']
            file_name = filename
            file_type = filename.rsplit('.', 1)[1].lower()
            file_url = file_path
            file_size = os.path.getsize(file_path)
            
            print(f"✅ File processed: {len(extracted_text)} characters")
            
        else:
            return jsonify({'error': 'No file or YouTube URL provided'}), 400
        
        # ✅ Final validation of extracted text
        if not extracted_text or len(extracted_text) < 50:
            return jsonify({
                'error': 'Document appears to be empty or too short. Please provide a document with at least 50 characters of text.',
                'extracted_length': len(extracted_text) if extracted_text else 0
            }), 400
        
        # Generate mentor identity using AI
        namer = AIMentorNamer()
        mentor_identity = namer.generate_mentor_identity(extracted_text, topic)
        
        # Create mentor in database
        deadline = datetime.now() + timedelta(days=int(target_days))
        
        mentor = LearningMentor(
            user_id=user_id,
            name=mentor_identity['name'],
            topic=topic or mentor_identity.get('expertise', 'General Knowledge'),
            avatar_emoji=mentor_identity['emoji'],
            personality=mentor_identity['personality'],
            target_days=int(target_days),
            deadline=deadline,
            total_messages=0,
            knowledge_points=0,
            current_streak=0
        )
        # ✅ ADD: Generate learning plan
        plan_generator = LearningPlanGenerator()
        learning_plan = plan_generator.generate_plan(
            document_text=extracted_text,
            topic=topic or mentor_identity.get('expertise', 'General Knowledge'),
            target_days=int(target_days)
        )
        
        # Save plan to mentor
        mentor.learning_plan = json.dumps(learning_plan)
        mentor.current_day = 1
     
        print(f"✅ Generated {learning_plan['total_days']}-day learning plan")
        
        db.add(mentor)
        db.flush()  # Get mentor ID
        
        # Create knowledge scroll entry
        scroll = KnowledgeScroll(
            mentor_id=mentor.id,
            file_name=file_name,
            file_type=file_type,
            file_url=file_url,
            file_size=file_size,
            extracted_text=extracted_text[:10000],  # Store first 10k chars
            summary=extracted_text[:500]  # Summary
        )
        
        db.add(scroll)
        db.commit()
        
        # Initialize mentor's knowledge graph
        kg = Neo4jKnowledgeGraph()
        kg.initialize_mentor_graph(mentor.id)
        
        # Add document to knowledge graph
        chunks_added = kg.add_document_to_graph(
            mentor_id=mentor.id,
            document_text=extracted_text,
            document_name=file_name
        )
        
        # Update scroll with processing info
        scroll.processed_at = datetime.now()
        db.commit()
        
        db.refresh(mentor)
        
        return jsonify({
            'success': True,
            'mentor': {
                'id': mentor.id,
                'name': mentor.name,
                'emoji': mentor.avatar_emoji,
                'topic': mentor.topic,
                'personality': mentor.personality,
                'teaching_style': mentor_identity.get('teaching_style', ''),
                'famous_quote': mentor_identity.get('famous_quote', ''),
                'deadline': mentor.deadline.isoformat(),
                'target_days': mentor.target_days,
                'scrolls': [{
                    'id': scroll.id,
                    'name': scroll.file_name,
                    'type': scroll.file_type,
                    'chunks': chunks_added
                }]
            }
        }), 201
        
    except Exception as e:
        print(f"Error creating mentor: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@mentors_bp.route('/list', methods=['GET'])
@require_auth
def list_mentors():
    """Get all mentors for current user"""
    try:
        db = SessionLocal()
        user_id = request.user_id
        
        print(f"📋 Listing mentors for user {user_id}")
        
        mentors = db.query(LearningMentor).filter(
            LearningMentor.user_id == user_id
        ).order_by(LearningMentor.last_message_at.desc().nullslast()).all()
        
        print(f"✅ Found {len(mentors)} mentors")
        
        result = []
        for mentor in mentors:
            scrolls = db.query(KnowledgeScroll).filter(
                KnowledgeScroll.mentor_id == mentor.id
            ).count()
            
            mentor_data = {
                'id': mentor.id,
                'name': mentor.name,
                'emoji': mentor.avatar_emoji,
                'topic': mentor.topic,
                'last_message': mentor.last_ai_message or "Ready to begin your journey?",
                'scrolls_count': scrolls,
                'streak': mentor.current_streak,
                'knowledge_points': mentor.knowledge_points,
                'created_at': mentor.created_at.isoformat()
            }
            
            print(f"  📖 Mentor: {mentor.name} (ID: {mentor.id})")
            result.append(mentor_data)
        
        return jsonify({'mentors': result})
        
    except Exception as e:
        print(f"❌ Error listing mentors: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()