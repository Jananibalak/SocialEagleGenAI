from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from extract_knowledge import KnowledgeExtractor

class GraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Clear all existing data"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database cleared")
    
    def create_entity(self, entity):
        """Create an entity node in Neo4j"""
        with self.driver.session() as session:
            # Use the entity type as the label (Person, Organization, Location, Product)
            query = f"""
            MERGE (e:{entity['type']} {{name: $name}})
            SET e += $properties
            RETURN e
            """
            session.run(query, name=entity['name'], properties=entity.get('properties', {}))
            print(f"  ✓ Created {entity['type']}: {entity['name']}")
    
    def create_relationship(self, relationship):
        """Create a relationship between entities"""
        with self.driver.session() as session:
            query = f"""
            MATCH (source {{name: $source_name}})
            MATCH (target {{name: $target_name}})
            MERGE (source)-[r:{relationship['type']}]->(target)
            SET r += $properties
            RETURN r
            """
            result = session.run(
                query,
                source_name=relationship['source'],
                target_name=relationship['target'],
                properties=relationship.get('properties', {})
            )
            if result.single():
                print(f"  ✓ Created relationship: {relationship['source']} --[{relationship['type']}]--> {relationship['target']}")
    
    def build_from_knowledge(self, knowledge):
        """Build graph from extracted knowledge"""
        print("\n--- Creating Entities ---")
        for entity in knowledge.get('entities', []):
            self.create_entity(entity)
        
        print("\n--- Creating Relationships ---")
        for relationship in knowledge.get('relationships', []):
            self.create_relationship(relationship)


# Main execution
if __name__ == "__main__":
    # Initialize
    extractor = KnowledgeExtractor()
    graph_builder = GraphBuilder(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    
    # Clear existing data
    graph_builder.clear_database()
    
    # Read the full knowledge base
    with open("knowledge_base.txt", "r") as f:
        text = f.read()
    
    # Process each paragraph separately
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
    print(f"\n📚 Processing {len(paragraphs)} paragraphs...\n")
    
    for i, paragraph in enumerate(paragraphs, 1):
        print(f"\n{'='*60}")
        print(f"Processing Paragraph {i}/{len(paragraphs)}")
        print(f"{'='*60}")
        print(f"{paragraph[:100]}...")
        
        # Extract knowledge
        knowledge = extractor.extract_from_text(paragraph)
        
        if knowledge:
            # Build graph
            graph_builder.build_from_knowledge(knowledge)
        else:
            print(f"⚠ Failed to extract knowledge from paragraph {i}")
    
    # Close connection
    graph_builder.close()
    
    print("\n" + "="*60)
    print("✅ Knowledge Graph Built Successfully!")
    print("="*60)
    print("\nVisualize it in Neo4j Browser:")
    print("1. Go to http://localhost:7474/browser/")
    print("2. Run: MATCH (n) RETURN n LIMIT 50")