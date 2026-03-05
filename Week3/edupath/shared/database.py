from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL Setup
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get PostgreSQL database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Neo4j Setup
class Neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        )
    
    def close(self):
        self.driver.close()
    
    def get_session(self):
        return self.driver.session()

# Global Neo4j connection
neo4j_conn = Neo4jConnection()

def get_neo4j():
    """Get Neo4j session"""
    return neo4j_conn.get_session()