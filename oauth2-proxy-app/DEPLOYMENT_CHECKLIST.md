# Production Deployment Checklist

## Security Updates v1.0.3

### ✅ Completed Before This Step
- [x] Password hashing migration (SHA256 → bcrypt)
- [x] JWT token authentication
- [x] Role-based access control
- [x] Default password update (view123 → SecureV1ew!2024)
- [x] Test suite updated and passing

### 🔧 Pre-Deployment Tasks

#### 1. Environment Configuration
```bash
# Create .env file with production values
cp .env.example .env

# Update these values in .env:
JWT_SECRET=your-32-or-more-char-random-secret-here
API_KEY_SECRET=another-32-char-secret-for-api-keys
ACCESS_TOKEN_EXPIRE_MINUTES=30  # or 15 for shorter expiry
BCRYPT_ROUNDS=12  # security tradeoff: higher = slower but more secure
```

#### 2. Verify Environment Variables
```bash
# Check all required env vars are set
grep -E "^(JWT_SECRET|API_KEY_SECRET|ACCESS_TOKEN_EXPIRE)" .env

# Verify secrets are at least 32 characters
echo "JWT_SECRET length: ${#JWT_SECRET}"  # Should be >= 32
```

#### 3. Database Migration (if applicable)
```bash
# Note: bcrypt hashes are incompatible with SHA256
# All users must re-authenticate

# Optional: Add migration script for password reset
# See: migration/password_reset.py
```

### 🚀 Deployment Steps

#### Option A: Docker Deployment
```bash
# Build and deploy
docker-compose up -d --build

# Verify deployment
curl http://localhost:8000/health
```

#### Option B: Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations (if any)
python -m alembic upgrade head

# Start application
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 🧪 Post-Deployment Verification

#### 1. Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Auth service health
curl http://localhost:8000/api/v1/health/auth

# Verify endpoints exist
curl -I http://localhost:8000/api/v1/auth/login
```

#### 2. Authentication Tests
```bash
# Test login with new default credentials
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=view&password=SecureV1ew!2024"

# Test admin login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=demo&password=D3mo!Admin@2024"
```

#### 3. Security Tests
```bash
# Run security tests
pytest tests/ -k "security" -v

# Run full test suite
pytest tests/
```

### ⚠️ Critical Actions Required

#### Before Users Can Access:
1. **Change default passwords** (IMMEDIATE)
   ```bash
   # Login as default admin, then change password
   # OR create new admin with unique password

   # Create new admin account:
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"newadmin","password":"YourNewSecurePassword123!","role":"admin"}'
   ```

2. **Notify all users** of password reset requirement
   - Email notification
   - Dashboard announcement
   - Documentation update

3. **Update documentation**
   - Password requirements
   - Reset procedures
   - Support contact info

#### Security Monitoring:
```bash
# Monitor for suspicious activity
# Check logs for:
- Failed login attempts
- Multiple IP addresses
- Token validation errors
- API key misuse
```

### 📋 User Communication Template

```
Subject: Important Security Update - Password Reset Required

Dear Users,

We have upgraded our security systems to use industry-standard
password encryption (bcrypt). This means all passwords must be
reset.

New Login:
- Username: view (viewer account)
- Password: SecureV1ew!2024

OR

- Username: demo (admin account)
- Password: D3mo!Admin@2024

Next Steps:
1. Login with credentials above
2. Change your password immediately
3. Use a strong password (8+ chars, mix of upper/lower/numbers/symbols)

If you have issues:
- Contact: support@example.com
- See: https://docs.example.com/password-reset

Thank you for helping keep our systems secure.

Best regards,
Security Team
```

### 🛠️ Troubleshooting

#### Issue: Login fails
```bash
# Check environment variables
echo $JWT_SECRET
echo $API_KEY_SECRET

# Verify bcrypt is working
python -c "from ai_app.auth_v2 import hash_password; print(hash_password('test'))"

# Check user exists
curl http://localhost:8000/api/v1/auth/me
```

#### Issue: Token validation errors
```bash
# Check JWT_SECRET is set
grep JWT_SECRET .env

# Restart application
docker-compose restart
```

#### Issue: Users cannot login
```bash
# Check default users initialized
python -c "from ai_app.auth_v2 import DEFAULT_USERS; print(list(DEFAULT_USERS.keys()))"

# Verify password hashes
python -c "from ai_app.auth_v2 import verify_password, get_user; print(verify_password('SecureV1ew!2024', get_user('view').password_hash))"
```

### 📊 Success Criteria

All of the following must pass:
- [x] Health endpoint returns 200
- [x] Login with default credentials succeeds
- [x] Token is returned in response
- [x] /me endpoint validates token
- [x] All security tests pass
- [x] No critical errors in logs
- [x] Users can log in and change passwords

### 🔄 Rollback Procedure

If deployment fails:
```bash
# Stop services
docker-compose down

# Restore last known good state
git checkout HEAD~1  # or appropriate commit

# Rebuild and restart
docker-compose up -d --build
```

### 📞 Support Contacts

- **Security Team**: security@example.com
- **DevOps Team**: devops@example.com
- **Documentation**: docs@example.com
- **Emergency**: +1-555-0000

---

**Deployment Date**: [YYYY-MM-DD]
**Deployment Team**: [Team Name]
**Version**: 1.0.3
