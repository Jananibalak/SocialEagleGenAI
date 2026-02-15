from setuptools import setup, find_packages

setup(
    name="edupath",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "flask-sqlalchemy>=3.0.0",
        "neo4j>=5.0.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "streamlit>=1.30.0",
        "plotly>=5.0.0",
        "pandas>=2.0.0",
        "requests>=2.31.0",
    ],
)