from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME
import json
from typing import Dict, List, Optional

# ============================================================================
# KNOWLEDGE EXTRACTION CLASS
# ============================================================================

class KnowledgeExtractor:
    """
    Extracts structured knowledge from unstructured text using LLMs
    
    Core Responsibilities:
    1. Connect to LLM API
    2. Build extraction prompts
    3. Parse LLM responses
    4. Handle errors gracefully
    5. Return structured knowledge (entities + relationships)
    
    Design Pattern: Single Responsibility Principle
    - This class only handles extraction, not storage
    - Separation of concerns = easier testing and maintenance
    """
    
    def __init__(self):
        """
        Initialize the extractor with API connection
        
        Process Flow:
        1. Create OpenAI client (configured for OpenRouter)
        2. Store client as instance variable for reuse
        
        Why store as self.client?
        - Reuse connection across multiple extractions
        - Avoid recreating client for each text chunk
        - More efficient (connection pooling)
        """
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,  # Point to OpenRouter instead of OpenAI
            api_key=OPENROUTER_API_KEY      # Your authentication
        )
        print("✓ Knowledge extractor initialized")
    
    # ========================================================================
    # CORE EXTRACTION METHOD
    # ========================================================================
    
    def extract_from_text(self, text: str) -> Optional[Dict]:
        """
        Extract entities and relationships from text using LLM
        
        Args:
            text (str): The text to analyze (paragraph, document chunk, etc.)
        
        Returns:
            Dict with structure:
            {
                "entities": [
                    {
                        "name": str,
                        "type": str,  # Person, Organization, Location, Product
                        "properties": dict
                    }
                ],
                "relationships": [
                    {
                        "source": str,      # Entity name
                        "target": str,      # Entity name
                        "type": str,        # Relationship type
                        "properties": {
                            "valid_from": str,  # Temporal validity start
                            "valid_to": str,    # Temporal validity end
                            "description": str
                        }
                    }
                ]
            }
            
            Returns None if extraction fails
        
        Process:
        1. Build prompt with instructions
        2. Send to LLM
        3. Parse JSON response
        4. Validate structure
        5. Return or handle errors
        """
        
        # ====================================================================
        # STEP 1: Build the Extraction Prompt
        # ====================================================================
        
        prompt = self._build_extraction_prompt(text)
        
        # ====================================================================
        # STEP 2: Call the LLM
        # ====================================================================
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,  # Deterministic output
                max_tokens=2000  # Limit response length
            )
            
            # ================================================================
            # STEP 3: Extract the Response Content
            # ================================================================
            
            result = response.choices[0].message.content
            
            # Why choices[0]?
            # LLMs can return multiple completions (if n > 1)
            # We always use the first one for consistency
            
            print(f"\n--- LLM Raw Response ---\n{result}\n")
            
            # ================================================================
            # STEP 4: Parse JSON Response
            # ================================================================
            
            knowledge = self._parse_json_response(result)
            
            if knowledge:
                self._validate_knowledge_structure(knowledge)
                return knowledge
            else:
                return None
                
        except Exception as e:
            print(f"✗ Error during extraction: {e}")
            return None
    
    # ========================================================================
    # PROMPT ENGINEERING METHODS
    # ========================================================================
    
    def _get_system_prompt(self) -> str:
        """
        Define the LLM's role and behavior
        
        System prompts are critical for:
        1. Setting expert persona
        2. Defining output format expectations
        3. Ensuring consistent behavior
        
        Best Practices:
        - Be specific about role
        - Emphasize output format
        - Keep it concise
        """
        return (
            "You are an expert knowledge graph extraction system. "
            "Your task is to analyze text and extract entities and relationships. "
            "CRITICAL: Always return valid JSON only, no markdown, no explanations. "
            "Be precise and extract temporal information when available."
        )
    
    def _build_extraction_prompt(self, text: str) -> str:
        """
        Build the detailed extraction instructions
        
        Prompt Engineering Strategy:
        1. Clear task definition
        2. Explicit output format (JSON schema)
        3. Examples and rules for edge cases
        4. Temporal relationship handling
        
        Why this structure works:
        - LLMs perform better with structured instructions
        - JSON schema ensures parseable output
        - Examples reduce ambiguity
        - Temporal rules capture time-based relationships
        """
        return f"""
Extract entities and relationships from the following text.

TEXT TO ANALYZE:
{text}

EXTRACTION RULES:

1. ENTITIES - Extract these types:
   - Person: Individual people (e.g., "Jeff Bezos", "Satya Nadella")
   - Organization: Companies, institutions (e.g., "Amazon", "Microsoft")
   - Location: Cities, countries, regions (e.g., "Seattle", "Washington")
   - Product: Products, services, brands (e.g., "AWS", "Azure")

2. RELATIONSHIPS - Extract connections with temporal validity:
   - Capture: FOUNDED, CEO_OF, WORKS_AT, LOCATED_IN, OWNS, LEADS, etc.
   - Include temporal data when mentioned in text

3. TEMPORAL INFORMATION:
   - If text says "until 2021" → valid_to: "2021"
   - If text says "since 2014" or "in 2014 became" → valid_from: "2014", valid_to: "present"
   - If text says "founded in 1994" → valid_from: "1994"
   - If no time mentioned → valid_from: null, valid_to: null

4. OUTPUT FORMAT (valid JSON only):
{{
  "entities": [
    {{
      "name": "Entity Name",
      "type": "Person|Organization|Location|Product",
      "properties": {{
        "key": "value",
        "founded": "year",
        "role": "position"
      }}
    }}
  ],
  "relationships": [
    {{
      "source": "Entity1 Name",
      "target": "Entity2 Name",
      "type": "RELATIONSHIP_TYPE",
      "properties": {{
        "valid_from": "YYYY|YYYY-MM-DD|null",
        "valid_to": "YYYY|YYYY-MM-DD|present|null",
        "description": "brief context"
      }}
    }}
  ]
}}

Return ONLY the JSON, no markdown formatting, no explanations.
"""
    
    # ========================================================================
    # RESPONSE PARSING METHODS
    # ========================================================================
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """
        Parse LLM response into Python dictionary
        
        Challenges:
        1. LLMs sometimes add markdown (```json ... ```)
        2. May include explanatory text
        3. JSON might be malformed
        
        Solution:
        1. Clean markdown formatting
        2. Attempt JSON parsing
        3. Handle errors gracefully
        
        Args:
            response: Raw text from LLM
            
        Returns:
            Parsed dictionary or None if parsing fails
        """
        try:
            # Remove markdown code blocks if present
            cleaned = response.strip()
            
            # Handle: ```json\n{...}\n```
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]  # Remove ```json
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]  # Remove ```
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]  # Remove trailing ```
            
            cleaned = cleaned.strip()
            
            # Parse JSON
            knowledge = json.loads(cleaned)
            
            return knowledge
            
        except json.JSONDecodeError as e:
            print(f"✗ JSON parsing error: {e}")
            print(f"  Attempted to parse: {response[:200]}...")
            return None
    
    def _validate_knowledge_structure(self, knowledge: Dict) -> bool:
        """
        Validate the extracted knowledge structure
        
        Validation checks:
        1. Required keys present (entities, relationships)
        2. Entities have required fields (name, type)
        3. Relationships have required fields (source, target, type)
        
        Why validate?
        - Catch LLM mistakes early
        - Ensure downstream code doesn't crash
        - Provide clear error messages
        
        Args:
            knowledge: Parsed knowledge dictionary
            
        Returns:
            True if valid, raises ValueError if not
        """
        # Check required top-level keys
        if "entities" not in knowledge or "relationships" not in knowledge:
            raise ValueError("Missing required keys: 'entities' or 'relationships'")
        
        # Validate entities
        for entity in knowledge.get("entities", []):
            if "name" not in entity or "type" not in entity:
                raise ValueError(f"Entity missing required fields: {entity}")
        
        # Validate relationships
        for rel in knowledge.get("relationships", []):
            if "source" not in rel or "target" not in rel or "type" not in rel:
                raise ValueError(f"Relationship missing required fields: {rel}")
        
        print(f"✓ Validated: {len(knowledge['entities'])} entities, {len(knowledge['relationships'])} relationships")
        return True

# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    """
    Test the knowledge extractor with sample text
    
    Purpose:
    - Verify API connection
    - Test extraction quality
    - Debug prompt effectiveness
    """
    
    print("="*70)
    print("KNOWLEDGE EXTRACTION TEST")
    print("="*70)
    
    # Initialize extractor
    extractor = KnowledgeExtractor()
    
    # Read sample text
    with open("knowledge_base.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    # Test with first paragraph
    first_paragraph = text.split("\n\n")[0]
    
    print(f"\nInput Text:\n{'-'*70}\n{first_paragraph}\n{'-'*70}\n")
    
    # Extract knowledge
    knowledge = extractor.extract_from_text(first_paragraph)
    
    if knowledge:
        print("\n" + "="*70)
        print("EXTRACTION RESULTS")
        print("="*70)
        
        # Display entities
        print("\nENTITIES:")
        print("-"*70)
        for entity in knowledge.get("entities", []):
            props = ", ".join([f"{k}: {v}" for k, v in entity.get("properties", {}).items()])
            print(f"  [{entity['type']}] {entity['name']}")
            if props:
                print(f"    Properties: {props}")
        
        # Display relationships
        print("\nRELATIONSHIPS:")
        print("-"*70)
        for rel in knowledge.get("relationships", []):
            props = rel.get("properties", {})
            
            # Format temporal info
            temporal = ""
            if props.get("valid_from") or props.get("valid_to"):
                valid_from = props.get("valid_from", "?")
                valid_to = props.get("valid_to", "?")
                temporal = f" [{valid_from} → {valid_to}]"
            
            print(f"  {rel['source']} --[{rel['type']}]--> {rel['target']}{temporal}")
            
            if props.get("description"):
                print(f"    Description: {props['description']}")
        
        print("\n" + "="*70)
        print("✓ Extraction completed successfully")
        print("="*70)
    else:
        print("\n✗ Extraction failed")