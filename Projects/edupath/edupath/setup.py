from setuptools import setup, find_packages

setup(
    name="edupath",
    version="1.0.0",
    description="AI-Powered Personal Learning Trainer",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "razorpay>=1.4.2",
        "neo4j>=5.15.0",
        "openai>=1.10.0",
        "python-dotenv>=1.0.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.9",
        "bcrypt>=4.1.2",
        "pyjwt>=2.8.0",
        "bleach>=6.1.0",
    ],
)
