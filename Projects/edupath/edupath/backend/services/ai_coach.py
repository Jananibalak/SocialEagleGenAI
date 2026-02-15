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
