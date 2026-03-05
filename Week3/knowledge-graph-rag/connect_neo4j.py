from neo4j import GraphDatabase

# Neo4j connection details
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "knowledge_graph_demo_2024"  # Change this to your actual password

# Create a driver instance
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Test the connection
def test_connection():
    try:
        driver.verify_connectivity()
        print("✓ Connection successful!")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

# Close the connection when done
def close_connection():
    driver.close()
    print("Connection closed")

# Run the test
if __name__ == "__main__":
    if test_connection():
        print("Neo4j is ready to use!")
        close_connection()