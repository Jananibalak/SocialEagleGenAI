# System Architecture

        ## Overview

        EduPath uses a microservices-inspired architecture with:

        - **Flask API** - REST backend
        - **PostgreSQL** - User data & transactions
        - **Neo4j** - Knowledge graph
        - **Redis** - Caching & rate limiting
        - **Razorpay** - Payment processing
        - **OpenRouter** - LLM API gateway

        ## Data Flow
```
        User → React Native → Flask API → PostgreSQL
                                        ↓
                                      Neo4j (Knowledge Graph)
                                        ↓
                                    OpenRouter (AI)
```

        ## Security Layers

        1. JWT Authentication
        2. Bcrypt Password Hashing
        3. Rate Limiting
        4. Input Validation
        5. CORS Configuration
        6. Webhook Signature Verification
