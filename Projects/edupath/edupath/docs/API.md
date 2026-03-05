# API Reference

        ## Base URL
```
        http://localhost:5000
```

        ## Authentication

        Most endpoints require JWT token:
```
        Authorization: Bearer <token>
```

        ## Endpoints

        ### Health Check
```
        GET /health
```

        Response:
```json
        {
          "status": "healthy"
        }
```

        ### Create User
```
        POST /api/auth/signup
```

        Body:
```json
        {
          "username": "janani",
          "email": "janani@example.com",
          "password": "SecurePass@123",
          "full_name": "Janani"
        }
```

        ### Login
```
        POST /api/auth/login
```

        Body:
```json
        {
          "email": "janani@example.com",
          "password": "SecurePass@123"
        }
```

        Response:
```json
        {
          "access_token": "eyJ...",
          "user_id": 1
        }
```
