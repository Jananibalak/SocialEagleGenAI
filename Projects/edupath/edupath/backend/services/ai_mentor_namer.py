from openai import OpenAI
import os
import json
import random

class AIMentorNamer:
    """Generate creative mentor names based on document content"""
    
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            default_headers={
                "HTTP-Referer": os.getenv("BACKEND_URL", "http://localhost:5000"),
                "X-Title": "EduPath Mentor Namer"
            }
        )
        self.model = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
    
    def generate_mentor_identity(self, document_text: str, topic: str = None) -> dict:
        """
        Generate mentor name, personality, and teaching style based on content
        
        Returns:
            {
                'name': 'Archimedes of Syracuse',
                'emoji': '⚙️',
                'personality': 'Brilliant inventor, loves practical applications',
                'teaching_style': 'hands-on, experimental, encourages discovery',
                'expertise': 'Mathematics, Physics, Engineering',
                'famous_quote': 'Give me a lever long enough...'
            }
        """
        
        # Truncate document for prompt (use first 3000 chars)
        content_sample = document_text[:3000] if len(document_text) > 3000 else document_text
        
        prompt = f"""You are a creative naming expert for an ancient book-themed learning app.

Based on the content below, generate a mentor identity inspired by famous historical scholars, inventors, or philosophers.

CONTENT TOPIC: {topic or "Not specified"}

CONTENT SAMPLE:
{content_sample}

Generate a mentor identity in JSON format with these fields:
1. "name" - A historical figure's name relevant to this topic (e.g., "Ada Lovelace", "Archimedes of Syracuse", "Marie Curie")
   - If it's a modern topic with no historical figure, create an ancient-sounding name (e.g., "Master Byticus" for programming)
2. "emoji" - One emoji representing their field (🧪🔬📐⚡🎨🔭📊🧮)
3. "personality" - Brief personality description (1 sentence)
4. "teaching_style" - How they teach (1 sentence)
5. "expertise" - Their area of expertise (few words)
6. "famous_quote" - A relevant quote (real or invented in their style)

Make it inspiring, ancient-sounding, and relevant to the content!

Return ONLY valid JSON, no other text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative mentor identity generator. Always return valid JSON only, no markdown, no backticks."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.9,  # High creativity
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            mentor_identity = json.loads(result_text)
            
            # Validate all required fields exist
            required_fields = ['name', 'emoji', 'personality', 'teaching_style', 'expertise']
            if all(field in mentor_identity for field in required_fields):
                return mentor_identity
            else:
                raise ValueError("Missing required fields in AI response")
                
        except Exception as e:
            print(f"AI naming error: {e}, using fallback")
            return self._fallback_mentor_identity(topic)
    
    def _fallback_mentor_identity(self, topic: str = None) -> dict:
        """Fallback mentor identity if AI fails"""
        
        fallback_mentors = [
            {
                'name': 'Socrates the Wise',
                'emoji': '🏛️',
                'personality': 'Questioner of everything, believes learning comes through dialogue',
                'teaching_style': 'Socratic method - guides through questions',
                'expertise': 'Philosophy, Critical Thinking',
                'famous_quote': 'The only true wisdom is knowing you know nothing'
            },
            {
                'name': 'Hypatia of Alexandria',
                'emoji': '📐',
                'personality': 'Brilliant mathematician, passionate about logic and reason',
                'teaching_style': 'Clear explanations, builds from fundamentals',
                'expertise': 'Mathematics, Astronomy, Philosophy',
                'famous_quote': 'Reserve your right to think, for even to think wrongly is better than not to think at all'
            },
            {
                'name': 'Leonardo da Vinci',
                'emoji': '🎨',
                'personality': 'Renaissance polymath, connects art and science',
                'teaching_style': 'Observational learning, sketching, experimentation',
                'expertise': 'Art, Engineering, Anatomy, Innovation',
                'famous_quote': 'Learning never exhausts the mind'
            },
            {
                'name': 'Ibn Sina (Avicenna)',
                'emoji': '📚',
                'personality': 'Persian polymath, systematic and thorough',
                'teaching_style': 'Structured curriculum, emphasis on understanding',
                'expertise': 'Medicine, Philosophy, Science',
                'famous_quote': 'Knowledge is the greatest of all possessions'
            }
        ]
        
        return random.choice(fallback_mentors)