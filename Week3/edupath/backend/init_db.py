from shared.database import engine, Base, neo4j_conn
from models.user import User, LearningSession, Goal

def init_postgresql():
    """Initialize PostgreSQL tables"""
    print("Creating PostgreSQL tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ PostgreSQL tables created")

def init_neo4j():
    """Initialize Neo4j constraints and indexes"""
    print("Setting up Neo4j constraints...")
    
    with neo4j_conn.get_session() as session:
        # Constraints
        constraints = [
            "CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE",
            "CREATE CONSTRAINT resource_id IF NOT EXISTS FOR (r:Resource) REQUIRE r.id IS UNIQUE",
        ]
        
        for constraint in constraints:
            try:
                session.run(constraint)
                print(f"✓ {constraint.split('FOR')[1].split('REQUIRE')[0].strip()}")
            except Exception as e:
                print(f"  (already exists or error: {e})")
        
        # Indexes
        indexes = [
            "CREATE INDEX concept_difficulty IF NOT EXISTS FOR (c:Concept) ON (c.difficulty)",
            "CREATE INDEX topic_category IF NOT EXISTS FOR (t:Topic) ON (t.category)",
        ]
        
        for index in indexes:
            try:
                session.run(index)
                print(f"✓ {index.split('FOR')[1].split('ON')[0].strip()}")
            except Exception as e:
                print(f"  (already exists or error: {e})")
    
    print("✓ Neo4j setup complete")

def seed_initial_concepts():
    """Seed some initial learning concepts for ML/AI"""
    print("\nSeeding initial concepts...")
    
    with neo4j_conn.get_session() as session:
        # Create main topics
        topics = [
            {"name": "Machine Learning", "category": "AI", "difficulty": "intermediate"},
            {"name": "Python Programming", "category": "Programming", "difficulty": "beginner"},
            {"name": "Mathematics", "category": "Foundation", "difficulty": "beginner"},
            {"name": "Data Science", "category": "AI", "difficulty": "intermediate"},
        ]
        
        for topic in topics:
            session.run("""
                MERGE (t:Topic {name: $name})
                SET t.category = $category,
                    t.difficulty = $difficulty
            """, **topic)
        
        # Create concepts with prerequisites
        concepts = [
            # Python basics
            {"name": "Variables", "topic": "Python Programming", "difficulty": 1, "prerequisites": []},
            {"name": "Functions", "topic": "Python Programming", "difficulty": 2, "prerequisites": ["Variables"]},
            {"name": "Lists", "topic": "Python Programming", "difficulty": 2, "prerequisites": ["Variables"]},
            {"name": "Loops", "topic": "Python Programming", "difficulty": 3, "prerequisites": ["Variables", "Lists"]},
            
            # Math basics
            {"name": "Linear Algebra", "topic": "Mathematics", "difficulty": 5, "prerequisites": []},
            {"name": "Calculus", "topic": "Mathematics", "difficulty": 6, "prerequisites": ["Linear Algebra"]},
            {"name": "Statistics", "topic": "Mathematics", "difficulty": 5, "prerequisites": []},
            {"name": "Probability", "topic": "Mathematics", "difficulty": 6, "prerequisites": ["Statistics"]},
            
            # ML concepts
            {"name": "Supervised Learning", "topic": "Machine Learning", "difficulty": 6, "prerequisites": ["Linear Algebra", "Python Programming"]},
            {"name": "Linear Regression", "topic": "Machine Learning", "difficulty": 5, "prerequisites": ["Supervised Learning", "Calculus"]},
            {"name": "Neural Networks", "topic": "Machine Learning", "difficulty": 8, "prerequisites": ["Linear Regression", "Calculus"]},
        ]
        
        for concept in concepts:
            # Create concept
            session.run("""
                MERGE (c:Concept {name: $name})
                SET c.difficulty = $difficulty
            """, name=concept["name"], difficulty=concept["difficulty"])
            
            # Link to topic
            session.run("""
                MATCH (c:Concept {name: $concept_name})
                MATCH (t:Topic {name: $topic_name})
                MERGE (c)-[:BELONGS_TO]->(t)
            """, concept_name=concept["name"], topic_name=concept["topic"])
            
            # Create prerequisite relationships
            for prereq in concept["prerequisites"]:
                # Check if prereq is a topic or concept
                if prereq in ["Python Programming", "Mathematics", "Machine Learning"]:
                    session.run("""
                        MATCH (c:Concept {name: $concept_name})
                        MATCH (t:Topic {name: $prereq_name})
                        MERGE (c)-[:REQUIRES_TOPIC]->(t)
                    """, concept_name=concept["name"], prereq_name=prereq)
                else:
                    session.run("""
                        MATCH (c:Concept {name: $concept_name})
                        MATCH (p:Concept {name: $prereq_name})
                        MERGE (c)-[:REQUIRES]->(p)
                    """, concept_name=concept["name"], prereq_name=prereq)
        
        print(f"✓ Seeded {len(topics)} topics and {len(concepts)} concepts")

if __name__ == "__main__":
    print("="*70)
    print("INITIALIZING EDUPATH DATABASE")
    print("="*70)
    
    init_postgresql()
    init_neo4j()
    seed_initial_concepts()
    
    print("\n" + "="*70)
    print("✓ Database initialization complete!")
    print("="*70)
    
    neo4j_conn.close()