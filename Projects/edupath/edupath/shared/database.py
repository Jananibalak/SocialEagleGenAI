from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./edupath.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Neo4j
class Neo4jConnection:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                auth=(
                    os.getenv("NEO4J_USERNAME", "neo4j"),
                    os.getenv("NEO4J_PASSWORD", "your_password")
                )
            )
        except Exception as e:
            print(f"Warning: Neo4j connection failed: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def get_session(self):
        if self.driver:
            return self.driver.session()
        return None

neo4j_conn = Neo4jConnection()
