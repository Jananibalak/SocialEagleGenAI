# 🎓 EduPath - AI-Powered Personal Learning Trainer

        An AI-powered learning platform with chatbot-first interface, built for Indian learners.

        ## ✨ Features

        - 🤖 **AI Coach** - GPT-4o-mini powered personalized guidance
        - 📅 **Daily Check-ins** - Morning motivation & evening reflections
        - 🔥 **Streak Tracking** - Gamified consistency
        - 📊 **Knowledge Graph** - Neo4j powered concept tracking
        - 💰 **Razorpay** - UPI, Cards, Net Banking (India-focused)
        - 🔐 **OWASP Compliant** - Production-grade security

        ## 🚀 Quick Start

        ### Prerequisites
        - Python 3.8+
        - Docker Desktop
        - Razorpay Account (https://razorpay.com)
        - OpenRouter API Key (https://openrouter.ai)

        ### Setup (5 minutes)
```bash
        # 1. Copy environment file
        cp .env.example .env
        # Edit .env with your API keys

        # 2. Start infrastructure
        docker-compose up -d

        # 3. Setup backend
        cd backend
        python -m venv venv
        source venv/bin/activate  # Windows: venv\Scripts\activate
        pip install -r requirements.txt

        # 4. Initialize databases
        python ../scripts/init_db.py
        python ../scripts/seed_concepts.py

        # 5. Run API
        python run_api.py
```

        API will be at: **http://localhost:5000**

        ## 📖 Documentation

        - [Setup Guide](docs/SETUP.md)
        - [API Reference](docs/API.md)
        - [Architecture](docs/ARCHITECTURE.md)
        - [Security](docs/SECURITY.md)

        ## 💰 Pricing (India)

        ### Token Packages
        - Starter: ₹499 (100 tokens)
        - Power: ₹1,999 (550 tokens) 🔥
        - Ultimate: ₹3,499 (1,200 tokens)

        ### Subscriptions
        - Free: 50 messages/month
        - Pro: ₹799/month (unlimited)
        - Pro Annual: ₹7,999/year

        ## 🧪 Testing

        **Razorpay Test Credentials:**
        - Card: 4111 1111 1111 1111
        - CVV: 123
        - UPI: success@razorpay

        ## 📄 License

        MIT License

        ## 🙏 Built With

        - Flask (Backend)
        - React Native (Frontend)
        - Neo4j (Knowledge Graph)
        - PostgreSQL (User Data)
        - Razorpay (Payments)
        - OpenRouter (AI/LLM)

        ---

        **Made with ❤️ in India 🇮🇳**
