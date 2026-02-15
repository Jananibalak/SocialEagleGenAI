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

        prompt = f"""
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
        """

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
        system_prompt = f"""
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
        """

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

        prompt = f"""
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
        """

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
    def chat_with_rag(self, user_message: str, context: str, mentor_info: Dict) -> str:
        """
        Chat with RAG (Retrieval-Augmented Generation)
        
        Args:
            user_message: User's question
            context: Retrieved context from knowledge base
            mentor_info: Mentor's personality and topic
            
        Returns:
            AI response based on context
        """
        
        # Build system prompt with mentor personality
        system_prompt = f"""You are {mentor_info['name']}, an expert mentor in {mentor_info['topic']}.

Your personality: {mentor_info.get('personality', 'Knowledgeable and encouraging')}

IMPORTANT INSTRUCTIONS:
1. You have access to the student's uploaded documents (scrolls of knowledge)
2. Use the CONTEXT provided below to answer questions accurately
3. If the context contains relevant information, reference it directly
4. If the context doesn't answer the question, use your general knowledge but mention you're going beyond the provided materials
5. Be encouraging and educational
6. Keep responses concise but thorough

CONTEXT FROM STUDENT'S DOCUMENTS:
{context if context else "(No relevant context found in uploaded materials)"}

Remember: You're teaching based on THEIR uploaded content. Stay true to what they provided."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=600
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ RAG chat error: {e}")
            return f"I encountered an error processing your question. Please try again. (Error: {str(e)})"

    def chat_with_plan(
            self, 
            user_message: str, 
            context: str, 
            mentor_info: Dict,
            learning_plan: Dict,
            current_day: int
        ) -> str:
            """
            Chat that follows the learning plan
            Gently redirects off-topic questions
            """
            
            # Get current day's plan
            current_day_plan = None
            if learning_plan and learning_plan.get('days'):
                for day_data in learning_plan['days']:
                    if day_data['day'] == current_day:
                        current_day_plan = day_data
                        break
            
            # Build system prompt with plan awareness
            system_prompt = f"""You are {mentor_info['name']}, an expert learning mentor in {mentor_info['topic']}.

    Your personality: {mentor_info.get('personality', 'Encouraging and structured')}

    LEARNING PLAN (Day {current_day} of {learning_plan.get('total_days', '?')}):
    {json.dumps(current_day_plan, indent=2) if current_day_plan else 'No plan for today'}

    TODAY'S OBJECTIVES:
    {chr(10).join(['- ' + obj for obj in current_day_plan.get('objectives', [])]) if current_day_plan else 'Study the materials'}

    IMPORTANT INSTRUCTIONS:
    1. **LEAD THE CONVERSATION** - You should guide the student through today's objectives
    2. **STAY ON TRACK** - If the student asks off-topic questions, gently redirect:
    - Acknowledge their curiosity
    - Explain we have a structured plan to achieve their goal
    - Offer to discuss that topic after completing today's objectives
    - Or ask if they want to modify the learning plan
    3. **USE THE CONTEXT** - Reference their uploaded materials
    4. **BE ENCOURAGING** - Celebrate progress, encourage persistence

    CONTEXT FROM STUDENT'S MATERIALS:
    {context if context else "(No relevant context)"}

    Remember: You're following a structured {learning_plan.get('total_days', '?')}-day plan to help them master {mentor_info['topic']}!"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=600
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                print(f"❌ Plan-aware chat error: {e}")
                return "I encountered an error. Let's continue with today's lesson!"
            
    def chat_with_plan_and_history(
        self, 
        user_message: str, 
        context: str, 
        mentor_info: Dict,
        learning_plan: Dict,
        current_day: int,
        conversation_history: List[Dict]
    ) -> str:
        """
        Chat with plan awareness AND conversation history
        """
        
        # Get current day's plan
        current_day_plan = None
        if learning_plan and learning_plan.get('days'):
            for day_data in learning_plan['days']:
                if day_data['day'] == current_day:
                    current_day_plan = day_data
                    break
        
        # Build system prompt
        system_prompt = f"""You are {mentor_info['name']}, an expert learning mentor in {mentor_info['topic']}.

Your personality: {mentor_info.get('personality', 'Encouraging and structured')}

LEARNING PLAN (Day {current_day} of {learning_plan.get('total_days', '?')}):
{json.dumps(current_day_plan, indent=2) if current_day_plan else 'No plan for today'}

TODAY'S OBJECTIVES:
{chr(10).join(['- ' + obj for obj in current_day_plan.get('objectives', [])]) if current_day_plan else 'Study the materials'}

IMPORTANT INSTRUCTIONS:
1. **MAINTAIN CONVERSATION FLOW** - Remember what was discussed previously
2. **RESPOND NATURALLY** - If the student says "hi" or greets you, greet them back warmly
3. **BUILD ON PREVIOUS CONTEXT** - Reference earlier parts of the conversation
4. **STAY ON TRACK** - Gently guide toward today's learning objectives
5. **BE CONVERSATIONAL** - This is a dialogue, not a lecture
6. **ACKNOWLEDGE THEIR INPUT** - Respond to what they actually said

If student asks off-topic:
- Acknowledge their curiosity
- Gently remind them of our learning goal
- Offer to discuss after completing today's objectives

CONTEXT FROM STUDENT'S MATERIALS:
{context if context else "(No relevant context)"}

You are following a {learning_plan.get('total_days', '?')}-day structured plan to help them master {mentor_info['topic']}."""

        # ✅ Build messages with conversation history
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=600
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Plan-aware chat with history error: {e}")
            return "I encountered an error. Let's continue with our lesson!"