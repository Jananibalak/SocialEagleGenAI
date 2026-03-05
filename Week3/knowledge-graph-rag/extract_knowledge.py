from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME
import json

class KnowledgeExtractor:
    def __init__(self):
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )
    
    def extract_from_text(self, text):
        """Extract entities and relationships from text using LLM"""
        
        prompt = f"""
You are a knowledge graph extraction expert. Extract entities and relationships from the following text.

Text: {text}

Extract:
1. Entities: People, Organizations, Locations, Products
2. Relationships: How entities are connected WITH temporal information

Return ONLY valid JSON in this exact format:
{{
  "entities": [
    {{"name": "Entity Name", "type": "Person|Organization|Location|Product", "properties": {{"key": "value"}}}}
  ],
  "relationships": [
    {{
      "source": "Entity1", 
      "target": "Entity2", 
      "type": "RELATIONSHIP_TYPE", 
      "properties": {{
        "valid_from": "YYYY or YYYY-MM-DD or null",
        "valid_to": "YYYY or YYYY-MM-DD or null or 'present'",
        "description": "brief description"
      }}
    }}
  ]
}}

IMPORTANT for temporal relationships:
- If the text mentions "until 2021", set valid_to: "2021"
- If the text mentions "since 2014" or "became in 2014", set valid_from: "2014", valid_to: "present"
- If the text mentions "founded in 1994", set valid_from: "1994"
- If no time information, set both to null

Be specific and accurate. Extract all important entities and relationships with their time periods.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a knowledge graph expert. Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            
            result = response.choices[0].message.content
            print(f"\n--- LLM Response ---\n{result}\n")
            
            # Parse JSON
            knowledge = json.loads(result)
            return knowledge
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Response was: {result}")
            return None
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return None


# Test the extractor
if __name__ == "__main__":
    extractor = KnowledgeExtractor()
    
    # Read sample text
    with open("knowledge_base.txt", "r") as f:
        text = f.read()
    
    # Extract first paragraph only for testing
    first_paragraph = text.split("\n\n")[0]
    print(f"Extracting knowledge from:\n{first_paragraph}\n")
    
    knowledge = extractor.extract_from_text(first_paragraph)
    
    if knowledge:
        print("\n--- Extracted Entities ---")
        for entity in knowledge.get("entities", []):
            print(f"  - {entity['name']} ({entity['type']})")
        
        print("\n--- Extracted Relationships (with temporal data) ---")
        for rel in knowledge.get("relationships", []):
            props = rel.get('properties', {})
            time_info = ""
            if props.get('valid_from') or props.get('valid_to'):
                time_info = f" [{props.get('valid_from', '?')} → {props.get('valid_to', '?')}]"
            print(f"  - {rel['source']} --[{rel['type']}]--> {rel['target']}{time_info}")
            if props.get('description'):
                print(f"    Description: {props['description']}")