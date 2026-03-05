import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# OpenRouter settings
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "openai/gpt-4o-mini"

# Verify configuration
def verify_config():
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found in .env file")
    if not NEO4J_PASSWORD:
        raise ValueError("NEO4J_PASSWORD not found in .env file")
    print("✓ Configuration loaded successfully")

if __name__ == "__main__":
    verify_config()