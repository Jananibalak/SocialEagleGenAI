from neo4j import GraphDatabase

# Connection details
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "knowledge_graph_demo_2024"  # Use your actual password

class KnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    # Clear all data (useful for testing)
    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database cleared")
    
    # Create a person node
    def create_person(self, name, age, role):
        with self.driver.session() as session:
            query = """
            CREATE (p:Person {name: $name, age: $age, role: $role})
            RETURN p
            """
            result = session.run(query, name=name, age=age, role=role)
            print(f"✓ Created person: {name}")
    
    # Create a company node
    def create_company(self, name, industry):
        with self.driver.session() as session:
            query = """
            CREATE (c:Company {name: $name, industry: $industry})
            RETURN c
            """
            result = session.run(query, name=name, industry=industry)
            print(f"✓ Created company: {name}")
    
    # Create a relationship: Person WORKS_AT Company
    def create_works_at_relationship(self, person_name, company_name):
        with self.driver.session() as session:
            query = """
            MATCH (p:Person {name: $person_name})
            MATCH (c:Company {name: $company_name})
            CREATE (p)-[:WORKS_AT]->(c)
            RETURN p, c
            """
            result = session.run(query, person_name=person_name, company_name=company_name)
            print(f"✓ Created relationship: {person_name} WORKS_AT {company_name}")
    
    # Query: Get all people and where they work
    def get_all_people_and_companies(self):
        with self.driver.session() as session:
            query = """
            MATCH (p:Person)-[:WORKS_AT]->(c:Company)
            RETURN p.name AS person, p.role AS role, c.name AS company
            """
            results = session.run(query)
            print("\n--- People and Companies ---")
            for record in results:
                print(f"{record['person']} ({record['role']}) works at {record['company']}")


# Main execution
if __name__ == "__main__":
    # Initialize knowledge graph
    kg = KnowledgeGraph(URI, USERNAME, PASSWORD)
    
    # Clear existing data
    kg.clear_database()
    
    # Create some people
    kg.create_person("Alice Smith", 30, "Data Scientist")
    kg.create_person("Bob Johnson", 35, "Software Engineer")
    kg.create_person("Carol Williams", 28, "Product Manager")
    
    # Create some companies
    kg.create_company("TechCorp", "Technology")
    kg.create_company("DataHub", "Analytics")
    
    # Create relationships
    kg.create_works_at_relationship("Alice Smith", "DataHub")
    kg.create_works_at_relationship("Bob Johnson", "TechCorp")
    kg.create_works_at_relationship("Carol Williams", "TechCorp")
    
    # Query the graph
    kg.get_all_people_and_companies()
    
    # Close connection
    kg.close()
    print("\n✓ Done!")