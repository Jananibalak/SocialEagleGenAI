from openai import OpenAI
import os
import json

class LearningPlanGenerator:
    """Generate structured learning plans from uploaded content"""
    
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.model = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
    
    def generate_plan(self, document_text: str, topic: str, target_days: int) -> dict:
        """
        Generate day-by-day learning plan with robust JSON handling
        
        Returns:
            dict with learning plan structure
        """
        
        # Sample document for plan generation (first 2000 chars)
        content_sample = document_text[:2000]
        
        prompt = f"""You are an expert learning coach creating a {target_days}-day study plan.

    TOPIC: {topic}

    CONTENT OVERVIEW:
    {content_sample}

    Create a structured {target_days}-day learning plan in JSON format.

    CRITICAL RULES:
    1. Use simple language without apostrophes or special characters
    2. Use "we will" instead of "we'll"
    3. Use "let us" instead of "let's" 
    4. Keep messages under 80 characters
    5. Avoid quotes and punctuation inside text

    JSON FORMAT:
    {{
    "total_days": {target_days},
    "topic": "{topic}",
    "days": [
    {{
        "day": 1,
        "title": "Day 1: Introduction",
        "objectives": ["Learn basics", "Understand concepts"],
        "key_concepts": ["fundamentals", "basics"],
        "estimated_time": "30 minutes",
        "mentor_message": "Welcome! Today we start with the basics."
    }},
    {{
        "day": 2,
        "title": "Day 2: Building Knowledge",
        "objectives": ["Deep dive", "Practice"],
        "key_concepts": ["applications", "examples"],
        "estimated_time": "45 minutes",
        "mentor_message": "Great work! Let us continue building."
    }}
    ]
    }}

    Create all {target_days} days. Keep it simple and clean.
    Return ONLY valid JSON, no markdown.
    """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a learning plan generator. Return ONLY valid JSON. Use simple language without contractions or apostrophes. Say 'let us' not 'let's', 'we will' not 'we'll', 'do not' not 'don't'."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # ✅ STEP 1: Remove markdown code fences
            if '```' in result_text:
                parts = result_text.split('```')
                for part in parts:
                    part = part.strip()
                    if part.startswith('json'):
                        result_text = part[4:].strip()
                        break
                    elif part.startswith('{'):
                        result_text = part
                        break
            
            # ✅ STEP 2: Clean up common JSON issues
            result_text = self._clean_json_string(result_text)
            
            # ✅ STEP 3: Parse JSON
            try:
                plan = json.loads(result_text)
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error at position {e.pos}: {e.msg}")
                
                # Show context around error
                start = max(0, e.pos - 50)
                end = min(len(result_text), e.pos + 50)
                print(f"📝 Problematic JSON snippet: ...{result_text[start:end]}...")
                
                # Try one more aggressive cleanup
                result_text = self._aggressive_json_cleanup(result_text)
                plan = json.loads(result_text)  # This will raise if still fails
            
            # ✅ STEP 4: Validate structure
            if not isinstance(plan, dict):
                raise ValueError("Plan is not a dictionary")
            
            if 'days' not in plan or not isinstance(plan['days'], list):
                raise ValueError("Plan missing 'days' array")
            
            if len(plan['days']) == 0:
                raise ValueError("Plan has no days")
            
            # ✅ STEP 5: Clean each day's text
            for day in plan['days']:
                if 'mentor_message' in day:
                    day['mentor_message'] = self._clean_text(day['mentor_message'])
                if 'title' in day:
                    day['title'] = self._clean_text(day['title'])
                if 'objectives' in day and isinstance(day['objectives'], list):
                    day['objectives'] = [self._clean_text(obj) for obj in day['objectives']]
            
            print(f"✅ Successfully generated {len(plan['days'])}-day learning plan")
            
            return plan
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"⚠️  Using fallback plan")
            return self._fallback_plan(topic, target_days)
            
        except Exception as e:
            print(f"❌ Error generating learning plan: {e}")
            print(f"⚠️  Using fallback plan")
            return self._fallback_plan(topic, target_days)

    def _clean_json_string(self, json_str: str) -> str:
        """Clean common JSON issues"""
        
        # Remove any BOM or weird characters at start
        json_str = json_str.strip().lstrip('\ufeff')
        
        # Replace smart quotes with regular quotes
        json_str = json_str.replace('"', '"').replace('"', '"')
        json_str = json_str.replace(''', "'").replace(''', "'")
        
        # Remove single quotes (should be double quotes in JSON)
        # But be careful not to break apostrophes in content
        
        return json_str

    def _aggressive_json_cleanup(self, json_str: str) -> str:
        """
        More aggressive cleanup for malformed JSON
        Fixes apostrophes breaking strings
        """
        
        # Fix the specific issue: "Let"s" -> "Let\\'s"
        # Find all strings and escape apostrophes inside them
        
        import re
        
        def escape_apostrophes_in_strings(match):
            """Escape apostrophes inside JSON strings"""
            content = match.group(1)
            # Escape apostrophes
            content = content.replace("'", "\\'")
            return f'"{content}"'
        
        # Match quoted strings and fix apostrophes inside
        # This regex finds: "content with ' apostrophe"
        json_str = re.sub(r'"([^"]*)"', escape_apostrophes_in_strings, json_str)
        
        return json_str

    def _clean_text(self, text: str) -> str:
        """Clean text content (remove problematic characters)"""
        if not isinstance(text, str):
            return text
        
        # Replace contractions with full forms
        replacements = {
            "let's": "let us",
            "Let's": "Let us",
            "we'll": "we will",
            "We'll": "We will",
            "you'll": "you will",
            "You'll": "You will",
            "don't": "do not",
            "Don't": "Do not",
            "won't": "will not",
            "Won't": "Will not",
            "can't": "cannot",
            "Can't": "Cannot",
            "it's": "it is",
            "It's": "It is",
            "that's": "that is",
            "That's": "That is",
            "here's": "here is",
            "Here's": "Here is",
            "there's": "there is",
            "There's": "There is",
        }
        
        for contraction, full_form in replacements.items():
            text = text.replace(contraction, full_form)
        
        # Remove any remaining problematic characters
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = ' '.join(text.split())  # Normalize whitespace
        
        return text

    def _fallback_plan(self, topic: str, target_days: int) -> dict:
        """Enhanced fallback plan if AI fails"""
        
        print(f"📚 Generating fallback {target_days}-day plan for {topic}")
        
        days = []
        
        # Split into weeks
        weeks = target_days // 7
        remaining_days = target_days % 7
        
        phase_names = [
            "Foundation", "Building Blocks", "Deep Dive", 
            "Advanced Concepts", "Mastery", "Practice", "Review"
        ]
        
        current_day = 1
        
        for week in range(weeks):
            phase = phase_names[min(week, len(phase_names) - 1)]
            
            for day_in_week in range(7):
                if current_day > target_days:
                    break
                
                days.append({
                    "day": current_day,
                    "title": f"Day {current_day}: {phase} - Part {day_in_week + 1}",
                    "objectives": [
                        f"Study {topic} fundamentals",
                        f"Practice {phase.lower()} concepts",
                        f"Review and consolidate knowledge"
                    ],
                    "key_concepts": [topic.lower(), phase.lower()],
                    "estimated_time": "30-45 minutes",
                    "mentor_message": f"Welcome to Day {current_day}! Today we focus on {phase.lower()}. Let's explore {topic} together."
                })
                
                current_day += 1
        
        # Add remaining days
        for remaining in range(remaining_days):
            if current_day > target_days:
                break
            
            days.append({
                "day": current_day,
                "title": f"Day {current_day}: {topic} - Final Review",
                "objectives": [f"Consolidate {topic} knowledge"],
                "key_concepts": [topic.lower()],
                "estimated_time": "30 minutes",
                "mentor_message": f"Day {current_day} - Keep up the great work!"
            })
            
            current_day += 1
        
        plan = {
            "total_days": target_days,
            "topic": topic,
            "days": days
        }
        
        print(f"✅ Generated fallback plan with {len(days)} days")
        
        return plan