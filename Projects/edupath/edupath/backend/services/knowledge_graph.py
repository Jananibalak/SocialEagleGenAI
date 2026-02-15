from typing import Dict, List, Optional
from shared.database import neo4j_conn
from datetime import datetime
import json

class KnowledgeGraphService:
    def __init__(self):
        self.driver = neo4j_conn.driver

    def get_user_knowledge_state(self, user_id: int) -> Dict:
        if not self.driver:
            return {"error": "Neo4j not available"}

        with self.driver.session() as session:
            mastered = self._get_mastered_concepts(session, user_id)
            in_progress = self._get_in_progress_concepts(session, user_id)
            ready = self._get_ready_to_learn(session, user_id, mastered)

            total_concepts = self._count_total_concepts(session)
            mastery_pct = (len(mastered) / total_concepts * 100) if total_concepts > 0 else 0

            return {
                "mastered_concepts": mastered,
                "in_progress_concepts": in_progress,
                "ready_to_learn": ready,
                "mastery_percentage": round(mastery_pct, 1),
                "total_concepts": total_concepts,
                "last_updated": datetime.now().isoformat()
            }

    def _get_mastered_concepts(self, session, user_id: int) -> List[str]:
        query = """
        MATCH (u:User {user_id: $user_id})-[m:MASTERED]->(c:Concept)
        WHERE m.mastery_level >= 8
        RETURN c.name as concept
        ORDER BY m.mastered_at DESC
        """

        result = session.run(query, user_id=user_id)
        return [record["concept"] for record in result]

    def _get_in_progress_concepts(self, session, user_id: int) -> List[Dict]:
        query = """
        MATCH (u:User {user_id: $user_id})-[l:LEARNING]->(c:Concept)
        WHERE l.mastery_level < 8
        RETURN 
            c.name as concept,
            c.difficulty as difficulty,
            l.mastery_level as current_mastery,
            l.sessions_count as sessions
        ORDER BY l.last_studied DESC
        """

        result = session.run(query, user_id=user_id)

        return [
            {
                "concept": record["concept"],
                "difficulty": record["difficulty"],
                "current_mastery": record["current_mastery"],
                "sessions_count": record["sessions"]
            }
            for record in result
        ]

    def _get_ready_to_learn(self, session, user_id: int, mastered: List[str]) -> List[Dict]:
        query = """
        MATCH (c:Concept)
        WHERE NOT EXISTS {
            MATCH (u:User {user_id: $user_id})-[:MASTERED|LEARNING]->(c)
        }
        OPTIONAL MATCH (c)-[:REQUIRES]->(prereq:Concept)
        WITH c, collect(prereq.name) as prerequisites
        WHERE all(p IN prerequisites WHERE p IN $mastered)
        RETURN 
            c.name as concept,
            c.difficulty as difficulty,
            prerequisites
        ORDER BY c.difficulty ASC
        LIMIT 10
        """

        result = session.run(query, user_id=user_id, mastered=mastered)

        return [
            {
                "concept": record["concept"],
                "difficulty": record["difficulty"],
                "prerequisites": record["prerequisites"]
            }
            for record in result
        ]

    def _count_total_concepts(self, session) -> int:
        result = session.run("MATCH (c:Concept) RETURN count(c) as total")
        return result.single()["total"]

    def update_concept_mastery(self, user_id: int, concept_name: str, session_data: Dict) -> Dict:
        if not self.driver:
            return {"error": "Neo4j not available"}

        with self.driver.session() as session:
            improvement = session_data["understanding_after"] - session_data["understanding_before"]

            query = """
            MATCH (u:User {user_id: $user_id})
            MERGE (c:Concept {name: $concept_name})
            MERGE (u)-[r:LEARNING]->(c)
            ON CREATE SET 
                r.mastery_level = 0,
                r.sessions_count = 0,
                r.started_at = datetime()
            SET 
                r.last_studied = datetime(),
                r.sessions_count = r.sessions_count + 1,
                r.mastery_level = CASE
                    WHEN $understanding_after >= 9 THEN 9.0
                    WHEN $understanding_after >= 8 THEN r.mastery_level + ($improvement * 0.5)
                    WHEN $understanding_after >= 6 THEN r.mastery_level + ($improvement * 0.3)
                    ELSE r.mastery_level + ($improvement * 0.1)
                END

            WITH u, c, r, r.mastery_level as old_mastery
            WHERE r.mastery_level >= 8 AND old_mastery < 8
            MERGE (u)-[m:MASTERED]->(c)
            SET m.mastered_at = datetime(),
                m.mastery_level = r.mastery_level

            RETURN 
                c.name as concept,
                old_mastery,
                r.mastery_level as new_mastery,
                r.mastery_level >= 8 as mastered
            """

            result = session.run(
                query,
                user_id=user_id,
                concept_name=concept_name,
                understanding_after=session_data["understanding_after"],
                improvement=improvement
            )

            record = result.single()

            return {
                "concept": record["concept"],
                "old_mastery": round(record["old_mastery"], 1),
                "new_mastery": round(record["new_mastery"], 1),
                "mastered": record["mastered"]
            }

def create_user_node(user_id: int, name: str):
    with neo4j_conn.driver.session() as session:
        session.run(
            """
            MERGE (u:User {user_id: $user_id})
            SET u.name = $name, u.created_at = datetime()
            """,
            user_id=user_id,
            name=name
        )
