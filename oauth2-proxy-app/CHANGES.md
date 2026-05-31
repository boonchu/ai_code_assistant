# Authentication Security Updates - Summary

## Release 1.0.3 (2024-05-30)

### Security Improvements

#### 1. Password Hashing: SHA256 → bcrypt
- **Before**: `hashlib.sha256()` - insecure, fast, no salt
- **After**: `bcrypt` - secure, slow, includes salt
- **Impact**: All existing passwords are incompatible; users must re-authenticate

#### 2. Secret Management
- **Before**: Hardcoded `SECRET_KEY` in source code
- **After**: Environment variable `JWT_SECRET`
- **Impact**: More secure configuration management

#### 3. New Files
- `ai_app/auth_v2.py` - Security-hardened authentication module
- `ai_app/routers/auth.py` - RESTful authentication endpoints
- `ai_app/routers/__init__.py` - Router initialization
- `AUTH_SECURITY.md` - Detailed security documentation

#### 4. Updated Files
- `ai_app/settings.py` - Added environment variable configuration
- `ai_app/proxy.py` - Removed duplicate authentication code

### Breaking Changes

1. **Import paths changed:**
   ```python
   # Old
   from ai_app.auth import ...

   # New
   from ai_app.auth_v2 import ...
   # or
   from ai_app.routers.auth import ...
   ```

2. **Password hashes incompatible:**
   - Old SHA256 hashes don't work with new bcrypt system
   - Users must log in again to get new hashes

3. **Endpoint structure:**
   - Authentication endpoints now in separate router
   - Prefix: `/api/v1/auth/*`

### Testing

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=view&password=view123"

# Get token
TOKEN="eyJ0eXAi..."

# Use token
curl "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

### Environment Variables

```bash
JWT_SECRET=your-secure-random-secret
API_KEY_SECRET=your-api-key
BCRYPT_ROUNDS=12
```

### Default Credentials

```
Username: view, Password: view123 (viewer role)
Username: demo, Password: admin123 (admin role)
```

⚠️ **Change these immediately in production!**

---

## Migration Steps

1. Set environment variables
2. Update Python imports
3. Reset user passwords
4. Test authentication flow
5. Update dependent applications

### Full Migration Guide

See `AUTH_SECURITY.md` for complete details.
