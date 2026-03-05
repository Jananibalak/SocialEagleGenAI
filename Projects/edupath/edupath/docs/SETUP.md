# Setup Guide

        ## Prerequisites

        - Python 3.8+
        - Docker Desktop
        - Razorpay Account
        - OpenRouter API Key

        ## Installation Steps

        ### 1. Environment Setup
```bash
        # Copy environment file
        cp .env.example .env

        # Edit .env and add your API keys
```

        ### 2. Start Infrastructure
```bash
        # Start PostgreSQL, Neo4j, Redis
        docker-compose up -d

        # Wait 10 seconds for startup
        sleep 10
```

        ### 3. Backend Setup
```bash
        cd backend

        # Create virtual environment
        python -m venv venv
        source venv/bin/activate  # Windows: venv\Scripts\activate

        # Install dependencies
        pip install -r requirements.txt

        # Initialize databases
        python ../scripts/init_db.py
        python ../scripts/seed_concepts.py
        python ../scripts/create_test_user.py

        # Start API
        python run_api.py
```

        ### 4. Test
```bash
        # Health check
        curl http://localhost:5000/health

        # Should return: {"status": "healthy"}
```

        ## Troubleshooting

        ### Database connection failed

        Check Docker containers:
```bash
        docker ps
```

        ### Module not found

        Install in editable mode:
```bash
        pip install -e .
```
