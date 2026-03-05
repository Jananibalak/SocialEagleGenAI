#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database import Base, engine, neo4j_conn
from backend.models.user import User, LearningSession

def init_postgresql():
    print("Initializing PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("✅ PostgreSQL tables created")

def init_neo4j():
    print("Initializing Neo4j...")
    session = neo4j_conn.get_session()
    if session:
        try:
            # Create constraints
            session.run(
                "CREATE CONSTRAINT concept_name IF NOT EXISTS "
                "FOR (c:Concept) REQUIRE c.name IS UNIQUE"
            )
            print("✅ Neo4j constraints created")
        finally:
            session.close()
    else:
        print("⚠️  Neo4j not available")

if __name__ == "__main__":
    print("=" * 70)
    print("INITIALIZING EDUPATH DATABASES")
    print("=" * 70)
    init_postgresql()
    init_neo4j()
    print("=" * 70)
    print("✅ Database initialization complete!")
    print("=" * 70)
