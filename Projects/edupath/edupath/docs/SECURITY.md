# Security Documentation

## OWASP Compliance

This project follows OWASP Top 10 guidelines.

### A01 - Broken Access Control

- JWT tokens (15-minute expiry)
- Role-based access control
- Protected routes

### A02 - Cryptographic Failures

- Bcrypt password hashing (12 rounds)
- TLS in production
- Secure token storage

### A03 - Injection

- Parameterized SQL queries
- Input sanitization
- XSS protection

## Best Practices

1. Never commit `.env` file
2. Use strong passwords
3. Enable 2FA (optional)
4. Regular security updates
5. Monitor audit logs
