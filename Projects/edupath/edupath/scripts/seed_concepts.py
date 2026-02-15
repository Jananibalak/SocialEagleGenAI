#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database import neo4j_conn

def seed_concepts():
    print("Seeding learning concepts...")
    session = neo4j_conn.get_session()

    if not session:
        print("⚠️  Neo4j not available")
        return

    try:
        concepts = [
            {"name": "Python Basics", "difficulty": 2},
            {"name": "Variables", "difficulty": 1},
            {"name": "Functions", "difficulty": 3},
            {"name": "Linear Algebra", "difficulty": 5},
            {"name": "Machine Learning", "difficulty": 7},
        ]

        for concept in concepts:
            session.run(
                "MERGE (c:Concept {name: $name}) "
                "SET c.difficulty = $difficulty",
                **concept
            )

        print(f"✅ Seeded {len(concepts)} concepts")
    finally:
        session.close()

if __name__ == "__main__":
    seed_concepts()
