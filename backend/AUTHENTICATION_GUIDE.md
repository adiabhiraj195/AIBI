# Authentication System Guide

## Overview
A complete database-based authentication system has been implemented for user login and signup functionality. The system uses:

- **PostgreSQL** for secure user storage
- **Bcrypt** for password hashing
- **JWT (JSON Web Tokens)** for stateless authentication
- **FastAPI** dependency injection for protected routes

---

## Features

### 1. **User Registration**
- Create new user accounts with email and username
- Password validation (minimum 8 characters)
- Duplicate email/username prevention
- Secure password hashing with bcrypt

### 2. **User Login**
- Authenticate with email and password
- Returns JWT access token
- Token includes user ID and email claims

### 3. **Protected Routes**
- Token-based authentication for sensitive endpoints
- Automatic token validation via dependency injection
- Extract current user from token

### 4. **Password Management**
- Change password with current password verification
- Password confirmation validation

### 5. **Token Verification**
- Verify token validity
- Check token expiration

---

## API Endpoints

### Authentication Endpoints (`/api/v1/auth`)

#### 1. **Register User** 
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "securepassword123",
  "confirm_password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "created_at": "2026-01-13T14:30:00"
  }
}
```

#### 2. **Login User**
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "created_at": "2026-01-13T14:30:00",
    "updated_at": "2026-01-13T14:30:00"
  }
}
```

#### 3. **Get Current User**
```
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "created_at": "2026-01-13T14:30:00",
  "updated_at": "2026-01-13T14:30:00"
}
```

#### 4. **Change Password**
```
POST /api/v1/auth/change-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "current_password": "securepassword123",
  "new_password": "newsecurepassword456",
  "confirm_password": "newsecurepassword456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully",
  "data": null
}
```

#### 5. **Verify Token**
```
POST /api/v1/auth/verify-token
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Token is valid",
  "data": {
    "user_id": 1,
    "email": "user@example.com",
    "username": "john_doe"
  }
}
```

#### 6. **Logout**
```
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logout successful. Please delete your token locally.",
  "data": null
}
```

---

## Using Protected Routes

To protect endpoints that require authentication, use the dependency injection:

```python
from fastapi import APIRouter, Depends
from app.models.user import UserResponse
from app.controllers.auth_controller import get_current_user

router = APIRouter()

@router.get("/protected-endpoint")
async def protected_endpoint(current_user: UserResponse = Depends(get_current_user)):
    """This endpoint is protected and requires valid authentication"""
    return {
        "message": f"Hello {current_user.username}",
        "user_id": current_user.id
    }
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

---

## Configuration

### Environment Variables (`.env`)
```env
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

**IMPORTANT**: Change `JWT_SECRET_KEY` in production to a strong, random value!

---

## How It Works

### Registration Flow
1. User submits email, username, and password
2. System validates input (password requirements, duplicates)
3. Password is hashed using bcrypt
4. User record created in database
5. Success response returned with user data

### Login Flow
1. User submits email and password
2. System retrieves user from database by email
3. Password compared against stored hash using bcrypt
4. If valid, JWT token created with user_id and email
5. Token and user data returned

### Protected Route Flow
1. Client sends request with `Authorization: Bearer {token}` header
2. `get_token_from_header` dependency extracts token
3. `get_current_user` dependency validates token
4. Token decoded to get user_id
5. User data retrieved from database
6. User object injected into route handler
7. Route handler executes with authenticated user context

---

## Security Considerations

1. **Password Hashing**: All passwords are hashed with bcrypt, not stored in plain text
2. **JWT Tokens**: Tokens contain only user_id and email, no sensitive data
3. **Token Expiration**: Tokens expire after 24 hours (configurable)
4. **HTTPS**: Always use HTTPS in production (not just HTTP)
5. **Secret Key**: Change `JWT_SECRET_KEY` in production
6. **CORS**: Already configured to allow cross-origin requests

---

## File Structure

```
app/
├── controllers/
│   └── auth_controller.py       # Authentication endpoints
├── models/
│   └── user.py                  # User Pydantic models
├── repositories/
│   └── user_repository.py       # Database operations
├── services/
│   └── auth_service.py          # Business logic
└── utils/
    └── auth.py                  # Password hashing & JWT utilities
```

---

## Testing the Authentication

### Using cURL

**Register:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "confirm_password": "testpass123"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

**Get Current User:**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Postman

1. Create POST request to `http://localhost:8000/api/v1/auth/register`
2. Set body to JSON with registration data
3. Copy `access_token` from response
4. In new request, add header: `Authorization: Bearer {access_token}`
5. Send authenticated requests

---

## Next Steps

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create users table** (automatically on startup):
   - The table is created automatically when the app starts
   - No manual migration needed

3. **Test endpoints** via FastAPI Swagger UI:
   - Open `http://localhost:8000/docs`
   - Try out all authentication endpoints

4. **Update protected routes**:
   - Add `Depends(get_current_user)` to any route that needs authentication
   - Access user data via injected `UserResponse` parameter

---

## Error Codes

- `400`: Bad request (validation error, duplicate email/username, password mismatch)
- `401`: Unauthorized (invalid credentials, expired token, missing token)
- `500`: Internal server error

---

For questions or issues, check the endpoint documentation in the FastAPI Swagger UI at `/docs`.
