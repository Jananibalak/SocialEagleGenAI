from typing import Dict, List, Optional, Set
from shared.database import neo4j_conn
from datetime import datetime
import json
from neo4j.time import DateTime

# Rest stays the same...

    # Add this helper function at the top of your file (after imports)
def serialize_neo4j_data(obj):
        """Convert Neo4j data types to JSON-serializable formats"""
        if isinstance(obj, dict):
            return {key: serialize_neo4j_data(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [serialize_neo4j_data(item) for item in obj]
        elif isinstance(obj, DateTime):
            # Convert Neo4j DateTime to ISO format string
            return obj.iso_format()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj


class KnowledgeGraphService:
    """
    Manages the learning knowledge graph in Neo4j
    
    Responsibilities:
    1. Track concept mastery for each user
    2. Find optimal learning paths
    3. Identify prerequisites and dependencies
    4. Suggest next topics to study
    5. Detect knowledge gaps
    6. Update mastery based on session results
    """
    
    def __init__(self):
        self.driver = neo4j_conn.driver
    
    # ═══════════════════════════════════════════════════════════════
    # USER KNOWLEDGE STATE
    # ═══════════════════════════════════════════════════════════════


    
    def get_user_knowledge_state(self, user_id: int) -> Dict:
        """
        Get comprehensive knowledge state for a user
        
        Returns:
        {
            "mastered_concepts": List[str],
            "in_progress_concepts": List[Dict],
            "ready_to_learn": List[Dict],
            "blocked_by_prerequisites": List[Dict],
            "knowledge_gaps": List[str],
            "mastery_percentage": float,
            "total_concepts": int
        }
        """
        
        with self.driver.session() as session:
            # Get mastered concepts
            mastered = self._get_mastered_concepts(session, user_id)
            
            # Get in-progress concepts
            in_progress = self._get_in_progress_concepts(session, user_id)
            
            # Get ready to learn (prerequisites met)
            ready = self._get_ready_to_learn(session, user_id, mastered)
            
            # Get blocked concepts
            blocked = self._get_blocked_concepts(session, user_id, mastered)
            
            # Calculate overall mastery
            total_concepts = self._count_total_concepts(session)
            mastery_pct = (len(mastered) / total_concepts * 100) if total_concepts > 0 else 0
            
            # Identify knowledge gaps
            gaps = self._identify_knowledge_gaps(session, user_id, mastered)
            
            return {
                "mastered_concepts": mastered,
                "in_progress_concepts": in_progress,
                "ready_to_learn": ready,
                "blocked_by_prerequisites": blocked,
                "knowledge_gaps": gaps,
                "mastery_percentage": round(mastery_pct, 1),
                "total_concepts": total_concepts,
                "last_updated": datetime.now().isoformat()
            }
    
    def _get_mastered_concepts(self, session, user_id: int) -> List[str]:
        """Get concepts the user has mastered"""
        
        query = """
        MATCH (u:User {user_id: $user_id})-[m:MASTERED]->(c:Concept)
        WHERE m.mastery_level >= 8
        RETURN c.name as concept
        ORDER BY m.mastered_at DESC
        """
        
        result = session.run(query, user_id=user_id)
        return [record["concept"] for record in result]
    
    def _get_in_progress_concepts(self, session, user_id: int) -> List[Dict]:
        """Get concepts user is currently learning"""
        
        query = """
        MATCH (u:User {user_id: $user_id})-[l:LEARNING]->(c:Concept)
        WHERE l.mastery_level < 8
        RETURN 
            c.name as concept,
            c.difficulty as difficulty,
            l.mastery_level as current_mastery,
            l.sessions_count as sessions,
            l.last_studied as last_studied
        ORDER BY l.last_studied DESC
        """
        
        result = session.run(query, user_id=user_id)
        
        return [
            {
                "concept": record["concept"],
                "difficulty": record["difficulty"],
                "current_mastery": record["current_mastery"],
                "sessions_count": record["sessions"],
                "last_studied": record["last_studied"]
            }
            for record in result
        ]
    
    def _get_ready_to_learn(
        self, 
        session, 
        user_id: int, 
        mastered: List[str]
    ) -> List[Dict]:
        """Get concepts that are ready to learn (prerequisites met)"""
        
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
            prerequisites,
            c.estimated_hours as estimated_hours
        ORDER BY c.difficulty ASC
        LIMIT 10
        """
        
        result = session.run(query, user_id=user_id, mastered=mastered)
        
        return [
            {
                "concept": record["concept"],
                "difficulty": record["difficulty"],
                "prerequisites": record["prerequisites"],
                "estimated_hours": record.get("estimated_hours", 2)
            }
            for record in result
        ]
    
    def _get_blocked_concepts(
        self,
        session,
        user_id: int,
        mastered: List[str]
    ) -> List[Dict]:
        """Get concepts blocked by missing prerequisites"""
        
        query = """
        MATCH (c:Concept)
        WHERE NOT EXISTS {
            MATCH (u:User {user_id: $user_id})-[:MASTERED|LEARNING]->(c)
        }
        MATCH (c)-[:REQUIRES]->(prereq:Concept)
        WHERE NOT prereq.name IN $mastered
        WITH c, collect(DISTINCT prereq.name) as missing_prereqs
        WHERE size(missing_prereqs) > 0
        RETURN 
            c.name as concept,
            c.difficulty as difficulty,
            missing_prereqs
        ORDER BY size(missing_prereqs) ASC
        LIMIT 10
        """
        
        result = session.run(query, user_id=user_id, mastered=mastered)
        
        return [
            {
                "concept": record["concept"],
                "difficulty": record["difficulty"],
                "missing_prerequisites": record["missing_prereqs"]
            }
            for record in result
        ]
    
    def _count_total_concepts(self, session) -> int:
        """Count total concepts in the graph"""
        
        result = session.run("MATCH (c:Concept) RETURN count(c) as total")
        return result.single()["total"]
    
    def _identify_knowledge_gaps(
        self,
        session,
        user_id: int,
        mastered: List[str]
    ) -> List[str]:
        """Identify important gaps in knowledge"""
        
        # Find commonly required prerequisites that user hasn't mastered
        query = """
        MATCH (c:Concept)-[:REQUIRES]->(prereq:Concept)
        WHERE NOT prereq.name IN $mastered
        WITH prereq.name as gap, count(*) as importance
        ORDER BY importance DESC
        LIMIT 5
        RETURN gap
        """
        
        result = session.run(query, mastered=mastered)
        return [record["gap"] for record in result]
    
    # ═══════════════════════════════════════════════════════════════
    # CONCEPT MASTERY TRACKING
    # ═══════════════════════════════════════════════════════════════
    
    def update_concept_mastery(
        self,
        user_id: int,
        concept_name: str,
        session_data: Dict
    ) -> Dict:
        """
        Update mastery level for a concept after a learning session
        
        Args:
            user_id: User ID
            concept_name: Name of concept studied
            session_data: {
                "understanding_before": int (1-10),
                "understanding_after": int (1-10),
                "duration_minutes": int,
                "difficulty_rating": int (1-10),
                "enjoyment_rating": int (1-10)
            }
        
        Returns:
            {
                "concept": str,
                "old_mastery": float,
                "new_mastery": float,
                "mastered": bool,
                "sessions_count": int
            }
        """
        
        with self.driver.session() as session:
            # Calculate new mastery level
            improvement = session_data["understanding_after"] - session_data["understanding_before"]
            
            # Get or create user-concept relationship
            query = """
            MATCH (u:User {user_id: $user_id})
            MERGE (c:Concept {name: $concept_name})
            MERGE (u)-[r:LEARNING]->(c)
            ON CREATE SET 
                r.mastery_level = 0,
                r.sessions_count = 0,
                r.total_minutes = 0,
                r.started_at = datetime()
            SET 
                r.last_studied = datetime(),
                r.sessions_count = r.sessions_count + 1,
                r.total_minutes = r.total_minutes + $duration
            
            WITH u, c, r, r.mastery_level as old_mastery
            
            // Update mastery level based on session performance
            SET r.mastery_level = CASE
                WHEN $understanding_after >= 9 THEN 
                    CASE WHEN r.mastery_level < 9 THEN 9.0 ELSE r.mastery_level END
                WHEN $understanding_after >= 8 THEN
                    r.mastery_level + ($improvement * 0.5)
                WHEN $understanding_after >= 6 THEN
                    r.mastery_level + ($improvement * 0.3)
                ELSE
                    r.mastery_level + ($improvement * 0.1)
            END
            
            // Cap at 10
            SET r.mastery_level = CASE 
                WHEN r.mastery_level > 10 THEN 10.0 
                ELSE r.mastery_level 
            END
            
            // Mark as mastered if level >= 8
            WITH u, c, r, old_mastery
            // Conditionally create MASTERED relationship if threshold reached
            FOREACH (ignored IN CASE WHEN r.mastery_level >= 8 AND old_mastery < 8 THEN [1] ELSE [] END |
                MERGE (u)-[m:MASTERED]->(c)
                SET m.mastered_at = datetime(),
                    m.mastery_level = r.mastery_level
            )
            
            RETURN 
                c.name as concept,
                old_mastery,
                r.mastery_level as new_mastery,
                r.sessions_count as sessions,
                r.mastery_level >= 8 as mastered
            """
            
            result = session.run(
                query,
                user_id=user_id,
                concept_name=concept_name,
                duration=session_data["duration_minutes"],
                understanding_after=session_data["understanding_after"],
                improvement=improvement
            )
            
            record = result.single()
            
            return {
                "concept": record["concept"],
                "old_mastery": round(record["old_mastery"], 1),
                "new_mastery": round(record["new_mastery"], 1),
                "mastered": record["mastered"],
                "sessions_count": record["sessions"]
            }
    
    # ═══════════════════════════════════════════════════════════════
    # LEARNING PATH GENERATION
    # ═══════════════════════════════════════════════════════════════
    
    def generate_learning_path(
        self,
        user_id: int,
        target_concept: str,
        max_depth: int = 10
    ) -> Dict:
        """
        Generate shortest learning path from current knowledge to target
        
        Uses Dijkstra's algorithm weighted by:
        - Concept difficulty
        - Estimated hours
        - Prerequisites
        
        Returns:
            {
                "target": str,
                "path": List[Dict],
                "total_estimated_hours": float,
                "prerequisites_met": bool,
                "next_step": str
            }
        """
        
        with self.driver.session() as session:
            # Get user's mastered concepts
            mastered = self._get_mastered_concepts(session, user_id)
            
            # Find shortest path considering prerequisites
            query = """
            MATCH (target:Concept {name: $target})
            
            // Find all prerequisites recursively
            OPTIONAL MATCH path = (target)-[:REQUIRES*]->(prereq:Concept)
            WHERE NOT prereq.name IN $mastered
            
            WITH target, 
                 collect(DISTINCT prereq.name) as unmet_prereqs,
                 collect(DISTINCT nodes(path)) as all_paths
            
            // Build ordered learning sequence
            UNWIND 
                CASE 
                    WHEN size(all_paths) = 0 THEN [[target]]
                    ELSE all_paths 
                END as path_nodes
            
            WITH target, unmet_prereqs, 
                 [node IN path_nodes | {
                     name: node.name,
                     difficulty: node.difficulty,
                     estimated_hours: coalesce(node.estimated_hours, 2)
                 }] as path_concepts
            
            // Reverse to get correct order (bottom-up)
            WITH target, unmet_prereqs, 
                 reverse(path_concepts) as ordered_path
            
            RETURN 
                target.name as target_concept,
                unmet_prereqs,
                ordered_path,
                reduce(total = 0, c IN ordered_path | total + c.estimated_hours) as total_hours
            """
            
            result = session.run(
                query,
                target=target_concept,
                mastered=mastered
            )
            
            record = result.single()
            
            if not record:
                return {"error": f"Concept '{target_concept}' not found"}
            
            path = record["ordered_path"]
            unmet_prereqs = record["unmet_prereqs"]
            
            # Filter out already mastered concepts from path
            path = [c for c in path if c["name"] not in mastered]
            
            return {
                "target": record["target_concept"],
                "path": path,
                "total_estimated_hours": round(record["total_hours"], 1),
                "prerequisites_met": len(unmet_prereqs) == 0,
                "missing_prerequisites": unmet_prereqs,
                "next_step": path[0]["name"] if path else "Already mastered!",
                "steps_remaining": len(path)
            }
    
    def find_shortest_path_between_concepts(
        self,
        concept_a: str,
        concept_b: str
    ) -> Dict:
        """
        Find connection between two concepts
        Useful for "how are X and Y related?"
        """
        
        with self.driver.session() as session:
            query = """
            MATCH (a:Concept {name: $concept_a})
            MATCH (b:Concept {name: $concept_b})
            MATCH path = shortestPath((a)-[*]-(b))
            RETURN 
                [node IN nodes(path) | node.name] as path_concepts,
                [rel IN relationships(path) | type(rel)] as relationship_types,
                length(path) as distance
            """
            
            result = session.run(query, concept_a=concept_a, concept_b=concept_b)
            record = result.single()
            
            if not record:
                return {
                    "connected": False,
                    "message": f"No connection found between {concept_a} and {concept_b}"
                }
            
            return {
                "connected": True,
                "path": record["path_concepts"],
                "relationships": record["relationship_types"],
                "distance": record["distance"]
            }
    
    # ═══════════════════════════════════════════════════════════════
    # RESOURCE LINKING
    # ═══════════════════════════════════════════════════════════════
    
    def link_resource_to_concept(
        self,
        resource_id: str,
        concept_names: List[str],
        resource_metadata: Dict
    ):
        """
        Link a learning resource (PDF, video, article) to concepts
        
        Args:
            resource_id: Unique resource identifier
            concept_names: Concepts covered in this resource
            resource_metadata: {
                "title": str,
                "type": str,  # pdf, video, article, book
                "url": str,
                "difficulty": int,
                "estimated_minutes": int
            }
        """
        
        with self.driver.session() as session:
            # Create resource node
            session.run("""
                MERGE (r:Resource {id: $resource_id})
                SET r.title = $title,
                    r.type = $type,
                    r.url = $url,
                    r.difficulty = $difficulty,
                    r.estimated_minutes = $estimated_minutes,
                    r.added_at = datetime()
            """, 
                resource_id=resource_id,
                **resource_metadata
            )
            
            # Link to concepts
            for concept in concept_names:
                session.run("""
                    MATCH (r:Resource {id: $resource_id})
                    MERGE (c:Concept {name: $concept})
                    MERGE (r)-[:TEACHES]->(c)
                """,
                    resource_id=resource_id,
                    concept=concept
                )
    
    def get_resources_for_concept(
        self,
        concept_name: str,
        resource_type: Optional[str] = None
    ) -> List[Dict]:
        """Get all resources that teach a concept"""
        
        with self.driver.session() as session:
            query = """
            MATCH (r:Resource)-[:TEACHES]->(c:Concept {name: $concept})
            """
            
            if resource_type:
                query += "WHERE r.type = $resource_type "
            
            query += """
            RETURN 
                r.id as id,
                r.title as title,
                r.type as type,
                r.url as url,
                r.difficulty as difficulty,
                r.estimated_minutes as estimated_minutes
            ORDER BY r.difficulty ASC
            """
            
            params = {"concept": concept_name}
            if resource_type:
                params["resource_type"] = resource_type
            
            result = session.run(query, **params)
            
            return [dict(record) for record in result]
    
    # ═══════════════════════════════════════════════════════════════
    # ANALYTICS
    # ═══════════════════════════════════════════════════════════════
    
    def get_learning_statistics(self, user_id: int) -> Dict:
        """Get comprehensive learning statistics"""
        
        with self.driver.session() as session:
            query = """
            MATCH (u:User {user_id: $user_id})
            OPTIONAL MATCH (u)-[m:MASTERED]->(mastered:Concept)
            OPTIONAL MATCH (u)-[l:LEARNING]->(learning:Concept)
            
            WITH u,
                 count(DISTINCT mastered) as mastered_count,
                 count(DISTINCT learning) as in_progress_count,
                 sum(l.sessions_count) as total_sessions,
                 sum(l.total_minutes) as total_minutes
            
            MATCH (c:Concept)
            WITH mastered_count, in_progress_count, total_sessions, total_minutes,
                 count(c) as total_concepts
            
            RETURN 
                mastered_count,
                in_progress_count,
                total_concepts,
                total_concepts - mastered_count - in_progress_count as not_started,
                total_sessions,
                total_minutes,
                (mastered_count * 1.0 / total_concepts * 100) as mastery_percentage
            """
            
            result = session.run(query, user_id=user_id)
            record = result.single()
            
            if not record:
                return {}
            
            return {
                "mastered_concepts": record["mastered_count"],
                "in_progress": record["in_progress_count"],
                "not_started": record["not_started"],
                "total_concepts": record["total_concepts"],
                "mastery_percentage": round(record["mastery_percentage"], 1),
                "total_sessions": record["total_sessions"] or 0,
                "total_learning_hours": round((record["total_minutes"] or 0) / 60, 1)
            }


# ═══════════════════════════════════════════════════════════════
# INITIALIZATION & TESTING
# ═══════════════════════════════════════════════════════════════

def create_user_node(user_id: int, name: str):
    """Create user node in graph (for testing)"""
    
    with neo4j_conn.driver.session() as session:
        session.run("""
            MERGE (u:User {user_id: $user_id})
            SET u.name = $name,
                u.created_at = datetime()
        """, user_id=user_id, name=name)
        print(f"✓ Created user node: {name} (ID: {user_id})")


if __name__ == "__main__":
    """Test the Knowledge Graph Service"""
    
    print("="*70)
    print("TESTING KNOWLEDGE GRAPH SERVICE")
    print("="*70)
    
    kg = KnowledgeGraphService()
    
    # Create test user
    test_user_id = 1
    create_user_node(test_user_id, "Janani")
    
    # Test 1: Get initial knowledge state
    print("\n[Test 1] Initial Knowledge State")
    print("-"*70)
    state = kg.get_user_knowledge_state(test_user_id)
    print(json.dumps(serialize_neo4j_data(state), indent=2))
    
    # Test 2: Update mastery after a session
    print("\n[Test 2] Update Concept Mastery")
    print("-"*70)
    mastery_update = kg.update_concept_mastery(
        user_id=test_user_id,
        concept_name="Variables",
        session_data={
            "understanding_before": 3,
            "understanding_after": 8,
            "duration_minutes": 45,
            "difficulty_rating": 4,
            "enjoyment_rating": 7
        }
    )
    print(json.dumps(serialize_neo4j_data(mastery_update), indent=2))
    
    # Test 3: Generate learning path
    print("\n[Test 3] Learning Path to Neural Networks")
    print("-"*70)
    path = kg.generate_learning_path(
        user_id=test_user_id,
        target_concept="Neural Networks"
    )
    print(json.dumps(path, indent=2))
    
    # Test 4: Get statistics
    print("\n[Test 4] Learning Statistics")
    print("-"*70)
    stats = kg.get_learning_statistics(test_user_id)
    print(json.dumps(stats, indent=2))
    
    print("\n" + "="*70)
    print("✓ Knowledge Graph Service tests complete!")
    print("="*70)

