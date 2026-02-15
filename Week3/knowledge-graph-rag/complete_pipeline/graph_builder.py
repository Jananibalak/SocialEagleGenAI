from neo4j import GraphDatabase
from typing import Dict, List, Optional
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

class GraphBuilder:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        try:
            self.driver.verify_connectivity()
            print("✓ Connected to Neo4j")
        except Exception as e:
            print(f"✗ Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        self.driver.close()
        print("✓ Neo4j connection closed")
    
    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database cleared")
    
    def get_database_stats(self) -> Dict:
        with self.driver.session() as session:
            node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
            labels = [record["label"] for record in session.run("CALL db.labels()")]
            rel_types = [record["relationshipType"] for record in session.run("CALL db.relationshipTypes()")]
            
            return {
                "nodes": node_count,
                "relationships": rel_count,
                "labels": labels,
                "relationship_types": rel_types
            }
    
    def create_entity(self, entity: Dict) -> bool:
        try:
            with self.driver.session() as session:
                entity_type = entity.get("type", "Entity")
                query = f"""
                MERGE (e:{entity_type} {{name: $name}})
                SET e += $properties
                RETURN e
                """
                result = session.run(
                    query,
                    name=entity["name"],
                    properties=entity.get("properties", {})
                )
                
                if result.single():
                    print(f"  ✓ [{entity_type}] {entity['name']}")
                    return True
                else:
                    return False
                    
        except Exception as e:
            print(f"  ✗ Error creating entity {entity.get('name')}: {e}")
            return False
    
    def batch_create_entities(self, entities: List[Dict]) -> int:
        success_count = 0
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                for entity in entities:
                    try:
                        entity_type = entity.get("type", "Entity")
                        query = f"""
                        MERGE (e:{entity_type} {{name: $name}})
                        SET e += $properties
                        RETURN e
                        """
                        tx.run(
                            query,
                            name=entity["name"],
                            properties=entity.get("properties", {})
                        )
                        success_count += 1
                    except Exception as e:
                        print(f"  ✗ Error in batch for {entity.get('name')}: {e}")
                tx.commit()
        
        print(f"✓ Batch created {success_count}/{len(entities)} entities")
        return success_count
    
    def create_relationship(self, relationship: Dict) -> bool:
        try:
            with self.driver.session() as session:
                rel_type = relationship["type"]
                query = f"""
                MATCH (source {{name: $source_name}})
                MATCH (target {{name: $target_name}})
                MERGE (source)-[r:{rel_type}]->(target)
                SET r += $properties
                RETURN r
                """
                result = session.run(
                    query,
                    source_name=relationship["source"],
                    target_name=relationship["target"],
                    properties=relationship.get("properties", {})
                )
                
                if result.single():
                    props = relationship.get("properties", {})
                    temporal = ""
                    if props.get("valid_from") or props.get("valid_to"):
                        valid_from = props.get("valid_from", "?")
                        valid_to = props.get("valid_to", "?")
                        temporal = f" [{valid_from} → {valid_to}]"
                    print(f"  ✓ {relationship['source']} --[{rel_type}]--> {relationship['target']}{temporal}")
                    return True
                else:
                    return False
                    
        except Exception as e:
            print(f"  ✗ Error creating relationship: {e}")
            return False
    
    def batch_create_relationships(self, relationships: List[Dict]) -> int:
        success_count = 0
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                for rel in relationships:
                    try:
                        rel_type = rel["type"]
                        query = f"""
                        MATCH (source {{name: $source_name}})
                        MATCH (target {{name: $target_name}})
                        MERGE (source)-[r:{rel_type}]->(target)
                        SET r += $properties
                        RETURN r
                        """
                        tx.run(
                            query,
                            source_name=rel["source"],
                            target_name=rel["target"],
                            properties=rel.get("properties", {})
                        )
                        success_count += 1
                    except Exception as e:
                        print(f"  ✗ Error in batch for {rel.get('source')} -> {rel.get('target')}: {e}")
                tx.commit()
        
        print(f"✓ Batch created {success_count}/{len(relationships)} relationships")
        return success_count
    
    def build_from_knowledge(self, knowledge: Dict) -> Dict:
        entities = knowledge.get("entities", [])
        relationships = knowledge.get("relationships", [])
        
        print("\n--- Creating Entities ---")
        entities_created = self.batch_create_entities(entities)
        
        print("\n--- Creating Relationships ---")
        relationships_created = self.batch_create_relationships(relationships)
        
        return {
            "entities_created": entities_created,
            "relationships_created": relationships_created
        }
    
    def find_entity(self, name: str) -> Optional[Dict]:
        with self.driver.session() as session:
            query = """
            MATCH (e {name: $name})
            RETURN e
            """
            result = session.run(query, name=name)
            record = result.single()
            
            if record:
                node = record["e"]
                return dict(node)
            return None
    
    def find_relationships_for_entity(self, entity_name: str, direction: str = "both") -> List[Dict]:
        with self.driver.session() as session:
            if direction == "outgoing":
                query = """
                MATCH (source {name: $name})-[r]->(target)
                RETURN source.name as source, type(r) as relationship, target.name as target, properties(r) as props
                """
            elif direction == "incoming":
                query = """
                MATCH (source)-[r]->(target {name: $name})
                RETURN source.name as source, type(r) as relationship, target.name as target, properties(r) as props
                """
            else:
                query = """
                MATCH (e {name: $name})-[r]-(other)
                RETURN e.name as entity, type(r) as relationship, other.name as connected, properties(r) as props
                """
            
            result = session.run(query, name=entity_name)
            return [dict(record) for record in result]
    
    def search_entities_by_type(self, entity_type: str) -> List[Dict]:
        with self.driver.session() as session:
            query = f"""
            MATCH (e:{entity_type})
            RETURN e.name as name, properties(e) as properties
            ORDER BY e.name
            """
            result = session.run(query)
            return [dict(record) for record in result]


if __name__ == "__main__":
    print("="*70)
    print("GRAPH BUILDER TEST")
    print("="*70)
    
    builder = GraphBuilder(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    builder.clear_database()
    
    test_knowledge = {
        "entities": [
            {"name": "Jeff Bezos", "type": "Person", "properties": {"role": "Founder"}},
            {"name": "Amazon", "type": "Organization", "properties": {"founded": 1994}},
            {"name": "Seattle", "type": "Location", "properties": {"state": "Washington"}}
        ],
        "relationships": [
            {
                "source": "Jeff Bezos",
                "target": "Amazon",
                "type": "FOUNDED",
                "properties": {"valid_from": "1994", "valid_to": "present"}
            }
        ]
    }
    
    stats = builder.build_from_knowledge(test_knowledge)
    print(f"\n✓ Test completed! Created {stats['entities_created']} entities, {stats['relationships_created']} relationships")
    builder.close()