# Authentication System - Quick Start

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

New packages added:
- `passlib[bcrypt]` - Password hashing
- `python-jose[cryptography]` - JWT token handling
- `email-validator` - Email validation

### 2. Update Environment Variables

Edit `.env` and ensure JWT configuration is set:
```env
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

**For Production:**
- Change `JWT_SECRET_KEY` to a strong random value (use `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

### 3. Start the Application

```bash
python main.py
```

The users table will be created automatically on startup.

## Quick Test

### 1. Open Swagger UI
Visit: http://localhost:8000/docs

### 2. Register a User
Click **POST /api/v1/auth/register** and try it out:
```json
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "SecurePass123",
  "confirm_password": "SecurePass123"
}
```

### 3. Login
Click **POST /api/v1/auth/login** and try it out:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

Copy the `access_token` from the response.

### 4. Test Protected Route
1. Click **GET /api/v1/auth/me**
2. Click the lock icon 🔒
3. Paste the token in the popup
4. Execute the request

## Key Files Created/Modified

### New Files:
- `app/models/user.py` - User models
- `app/controllers/auth_controller.py` - Authentication endpoints
- `app/repositories/user_repository.py` - User database operations
- `app/services/auth_service.py` - Authentication business logic
- `app/utils/auth.py` - Password hashing & JWT utilities
- `migrations_auth.sql` - Database schema
- `AUTHENTICATION_GUIDE.md` - Complete documentation

### Modified Files:
- `main.py` - Added auth router and users table initialization
- `app/config.py` - Added JWT configuration
- `.env` - Added JWT settings
- `requirements.txt` - Added authentication packages

## Authentication Architecture

```
Request → Auth Controller → Auth Service → User Repository → Database
                  ↓
           Middleware validates JWT token
                  ↓
         Injects UserResponse into route handler
```

## Using Authentication in Other Endpoints

To protect any endpoint with authentication:

```python
from fastapi import APIRouter, Depends
from app.controllers.auth_controller import get_current_user
from app.models.user import UserResponse

@router.post("/protected-endpoint")
async def protected_endpoint(current_user: UserResponse = Depends(get_current_user)):
    """This endpoint requires authentication"""
    return {
        "message": f"Hello {current_user.username}",
        "user_id": current_user.id,
        "user_email": current_user.email
    }
```

## Available Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:------------:|
| POST | `/api/v1/auth/register` | Register new user | ❌ |
| POST | `/api/v1/auth/login` | Login and get token | ❌ |
| GET | `/api/v1/auth/me` | Get current user | ✅ |
| POST | `/api/v1/auth/change-password` | Change password | ✅ |
| POST | `/api/v1/auth/verify-token` | Verify token validity | ✅ |
| POST | `/api/v1/auth/logout` | Logout user | ✅ |

## How to Use the Token

Add to request headers:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Example with cURL:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/auth/me
```

### Example with Python:
```python
import requests

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(
    "http://localhost:8000/api/v1/auth/me",
    headers=headers
)
```

### Example with JavaScript:
```javascript
const response = await fetch('http://localhost:8000/api/v1/auth/me', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${access_token}`
    }
});
```

## Security Best Practices

✅ **Do:**
- Use HTTPS in production
- Store tokens in httpOnly cookies (frontend)
- Refresh tokens periodically
- Change JWT_SECRET_KEY in production
- Use strong passwords (8+ characters recommended)
- Hash passwords with bcrypt

❌ **Don't:**
- Store tokens in localStorage (vulnerable to XSS)
- Commit JWT_SECRET_KEY to version control
- Use the default JWT_SECRET_KEY in production
- Send tokens in URL parameters
- Store passwords in plain text

## Troubleshooting

### "Table users does not exist"
- Solution: Restart the app. The table is created automatically on startup.

### "Invalid token" error
- Ensure token is not expired
- Check token format: `Authorization: Bearer {token}`
- Verify JWT_SECRET_KEY matches in config

### "Email already registered"
- User with that email already exists
- Use login instead or try a different email

### "Invalid email or password"
- Email and password combination doesn't match
- Check for typos
- Verify user is registered first

## What's Next?

1. **Protect existing endpoints**: Add `Depends(get_current_user)` to CSV endpoints
2. **Add user verification**: Send verification emails
3. **Implement refresh tokens**: Extend session duration
4. **Add role-based access**: Admin, user, viewer roles
5. **Rate limiting**: Prevent brute force attacks

See `AUTHENTICATION_GUIDE.md` for complete documentation.
