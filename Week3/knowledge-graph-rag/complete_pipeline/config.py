import os
from dotenv import load_dotenv

# ============================================================================
# STEP 1: Load Environment Variables
# ============================================================================
# Why? Security! Never hardcode API keys in your code
# .env file keeps secrets separate from code
load_dotenv()

# ============================================================================
# STEP 2: Define Configuration Constants
# ============================================================================

# --- OpenRouter Configuration ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# What: Your secret key to access OpenRouter's API
# Why: Authentication - proves you're authorized to use the service
# How it works: Sent in HTTP headers with every request

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# What: The endpoint where we send API requests
# Why: OpenRouter acts as a gateway to multiple AI models
# Alternative: Could use "https://api.openai.com/v1" for direct OpenAI access

MODEL_NAME = "openai/gpt-4o-mini"
# What: Specific AI model identifier
# Why: Different models have different capabilities/costs
# Options: 
#   - "openai/gpt-4o-mini" (cheap, fast)
#   - "openai/gpt-4o" (more capable, expensive)
#   - "anthropic/claude-3-opus" (different provider)

# --- Neo4j Configuration ---
NEO4J_URI = os.getenv("NEO4J_URI")
# What: Connection string to your Neo4j database
# Format: "bolt://hostname:port" or "neo4j://hostname:port"
# bolt:// = Binary protocol for Neo4j (faster)
# Example: "bolt://localhost:7687"

NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
# What: Database username (usually "neo4j")
# Why: Access control - who can access the database

NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
# What: Database password
# Why: Security - protects your data

# ============================================================================
# STEP 3: Configuration Validation
# ============================================================================
def verify_config():
    """
    Validates that all required configuration is present
    
    Process:
    1. Check each critical config value
    2. If missing, raise descriptive error
    3. If all present, confirm success
    
    Why this matters:
    - Fail fast: Catch config errors before processing starts
    - Clear errors: Tell user exactly what's missing
    - Prevents cryptic failures later in the pipeline
    """
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY not found in .env file\n"
            "Get your key at: https://openrouter.ai/keys"
        )
    
    if not NEO4J_PASSWORD:
        raise ValueError(
            "NEO4J_PASSWORD not found in .env file\n"
            "Set this in your .env file or Neo4j Desktop"
        )
    
    if not NEO4J_URI:
        raise ValueError(
            "NEO4J_URI not found in .env file\n"
            "Default should be: bolt://localhost:7687"
        )
    
    print("✓ Configuration loaded successfully")
    print(f"  - Model: {MODEL_NAME}")
    print(f"  - Neo4j: {NEO4J_URI}")

# ============================================================================
# STEP 4: Test Configuration
# ============================================================================
if __name__ == "__main__":
    """
    This block only runs when you execute: python config.py
    Not when you import this file into another script
    
    Purpose: Quick config validation without running main app
    """
    verify_config()
