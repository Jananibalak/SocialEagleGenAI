import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

print("="*70)
print("TESTING OPENROUTER CONNECTION")
print("="*70)

# Check if API key exists
api_key = os.getenv("OPENROUTER_API_KEY")
print(f"\n1. API Key Check:")
if api_key:
    print(f"   ✓ API key found: {api_key[:20]}...")
else:
    print(f"   ✗ API key NOT found in .env file")
    print(f"   → Please add OPENROUTER_API_KEY to your .env file")
    exit(1)

# Try to connect
print(f"\n2. Testing API Connection:")
try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "EduPath Test"
        }
    )
    
    # Make a simple test call
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Say 'Hello from EduPath!' and nothing else."}
        ],
        max_tokens=20
    )
    
    result = response.choices[0].message.content
    print(f"   ✓ Connection successful!")
    print(f"   Response: {result}")
    
except Exception as e:
    print(f"   ✗ Connection failed: {e}")
    print(f"\n   Troubleshooting:")
    print(f"   1. Check your API key is valid at https://openrouter.ai/keys")
    print(f"   2. Ensure you have credits in your OpenRouter account")
    print(f"   3. Try creating a new API key")
    exit(1)

print("\n" + "="*70)
print("✓ All tests passed! You're ready to use the AI Coach.")
print("="*70)