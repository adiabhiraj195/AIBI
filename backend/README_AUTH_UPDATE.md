# Authentication System - README Update

Add this section to your main `README.md`:

---

## 🔐 Authentication System

The application now includes a complete database-based authentication system for user login and signup.

### Features
- ✅ User registration with email and username
- ✅ Secure password hashing with bcrypt
- ✅ JWT-based authentication tokens
- ✅ Protected API endpoints
- ✅ Password change functionality
- ✅ Token verification and validation

### Quick Start

#### 1. Install Authentication Dependencies
```bash
pip install -r requirements.txt
```

New dependencies:
- `passlib[bcrypt]` - Password hashing
- `python-jose[cryptography]` - JWT tokens
- `email-validator` - Email validation

#### 2. Configure JWT Settings
Edit `.env`:
```env
JWT_SECRET_KEY=change-this-to-a-strong-secret-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

#### 3. Start the Application
```bash
python main.py
```

The `users` table will be created automatically on first run.

### Authentication Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|:-------------|
| `/api/v1/auth/register` | POST | Register new user | ❌ |
| `/api/v1/auth/login` | POST | Login and get token | ❌ |
| `/api/v1/auth/me` | GET | Get current user info | ✅ |
| `/api/v1/auth/change-password` | POST | Change password | ✅ |
| `/api/v1/auth/verify-token` | POST | Verify token validity | ✅ |
| `/api/v1/auth/logout` | POST | Logout user | ✅ |

### Example Usage

#### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "password": "SecurePass123",
    "confirm_password": "SecurePass123"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

Response includes `access_token`.

#### Access Protected Endpoint
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer {access_token}"
```

### Using Authentication in Your Routes

Protect any endpoint by adding `get_current_user` dependency:

```python
from fastapi import APIRouter, Depends
from app.controllers.auth_controller import get_current_user
from app.models.user import UserResponse

router = APIRouter()

@router.post("/api/v1/protected-endpoint")
async def protected_endpoint(current_user: UserResponse = Depends(get_current_user)):
    """This endpoint requires authentication"""
    return {
        "message": f"Hello {current_user.username}",
        "user_id": current_user.id
    }
```

### Documentation

- **Quick Start**: See `AUTH_QUICKSTART.md`
- **Complete Guide**: See `AUTHENTICATION_GUIDE.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Code Examples**: See `examples/auth_examples.py`

### Security Notes

- 🔒 Passwords are hashed with bcrypt (not stored in plain text)
- 🔐 JWT tokens expire after 24 hours (configurable)
- 🛡️ Use HTTPS in production
- ⚠️ Change `JWT_SECRET_KEY` in production environment
- 📝 Store tokens securely on client (httpOnly cookies recommended)

### Testing

1. **Interactive API Docs** (Swagger UI):
   - Open `http://localhost:8000/docs`
   - Try endpoints directly in browser

2. **Run Examples**:
   ```bash
   python examples/auth_examples.py
   ```

3. **Command Line** (using cURL or Postman):
   - See example cURL commands above

### Database Schema

Automatically created on startup:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

For more detailed information, see the documentation files mentioned above.
