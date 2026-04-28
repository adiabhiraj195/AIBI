# Complete Authentication System Guide

This document provides a comprehensive guide to the authentication system implemented in the CFO Multi-Agent Chatbot Frontend application.

## Overview

The authentication system includes:
- **User Registration** - Create new accounts
- **User Login** - Authenticate with email/username
- **Change Password** - Update user password securely
- **Protected Routes** - Restrict access to authenticated users
- **Token Management** - JWT-based token storage and validation

---

## Pages & Routes

### 1. **Login Page** (`/login`)
**Path:** `src/pages/LoginPage.tsx`

**Features:**
- Email or username login field
- Password input with icon
- Form validation
- Loading state during submission
- Error message display
- Link to registration page
- Responsive design with gradient background

**Theme:** Blue/Indigo gradient with modern card design

**Example Usage:**
```bash
Navigate to: http://localhost:5173/login
```

---

### 2. **Register Page** (`/register`)
**Path:** `src/pages/RegisterPage.tsx`

**Features:**
- Email input with validation
- Username field (minimum 3 characters)
- Password field (minimum 8 characters)
- Password confirmation
- Real-time form validation
- Success screen with auto-redirect to login
- Error handling with detailed messages

**Theme:** Green/Emerald gradient for registration success feedback

**Validation Rules:**
- Email: Valid email format required
- Username: Minimum 3 characters
- Password: Minimum 8 characters
- Confirm Password: Must match password field

**Example Usage:**
```bash
Navigate to: http://localhost:5173/register
```

---

### 3. **Change Password Page** (`/change-password`)
**Path:** `src/pages/ChangePasswordPage.tsx`

**Features:**
- Current password verification
- New password input
- Password confirmation
- Back to dashboard button
- Password requirements display
- Success confirmation screen
- Protected route (requires authentication)

**Theme:** Blue/Indigo matching dashboard theme

**Validation Rules:**
- Current password: Required
- New password: Minimum 8 characters, must be different from current
- Confirm password: Must match new password

**Example Usage:**
```bash
Navigate to: http://localhost:5173/change-password
(Requires authentication)
```

---

## API Service Layer

**Location:** `src/services/api.ts`

### Authentication Functions

#### 1. **login(credentials: LoginRequest)**
Authenticates user and returns access token.

```typescript
const response = await login({
  identifier: 'user@example.com', // or username
  password: 'password123'
});
// Returns: { access_token, token_type, user }
```

#### 2. **register(credentials: RegisterRequest)**
Creates new user account.

```typescript
const response = await register({
  email: 'newuser@example.com',
  username: 'newuser',
  password: 'securepass123',
  confirm_password: 'securepass123'
});
// Returns: { success: boolean, message: string, data: userData }
```

#### 3. **changePassword(passwords: ChangePasswordRequest)**
Updates user password.

```typescript
const response = await changePassword({
  current_password: 'oldpass123',
  new_password: 'newpass456',
  confirm_password: 'newpass456'
});
// Returns: { success: boolean, message: string }
```

#### 4. **getCurrentUser()**
Fetches current authenticated user data.

```typescript
const user = await getCurrentUser();
// Returns: User object with id, email, username, etc.
```

#### 5. **verifyToken()**
Validates current authentication token.

```typescript
const result = await verifyToken();
// Returns: { success: boolean, data: { user_id, email, username } }
```

#### 6. **logout()**
Clears stored credentials.

```typescript
logout();
// Removes token and user from localStorage
```

### Token Management Functions

#### **getAuthToken()**
Returns stored JWT token.
```typescript
const token = getAuthToken();
```

#### **setAuthToken(token: string)**
Stores JWT token in localStorage.
```typescript
setAuthToken('jwt_token_here');
```

#### **getAuthUser()**
Returns stored user data.
```typescript
const user = getAuthUser();
```

#### **setAuthUser(user: User)**
Stores user data in localStorage.
```typescript
setAuthUser(userData);
```

#### **isAuthenticated()**
Checks if user is authenticated.
```typescript
if (isAuthenticated()) {
  // User is logged in
}
```

#### **getAuthHeader()**
Returns authorization header for API requests.
```typescript
const headers = getAuthHeader();
// Returns: { Authorization: 'Bearer token' } or {}
```

---

## Authentication Context

**Location:** `src/context/AuthContext.tsx`

### useAuth Hook

Access authentication state and functions in any component:

```typescript
import { useAuth } from '../context/AuthContext';

function MyComponent() {
  const { 
    user, 
    accessToken, 
    isAuthenticated, 
    isLoading,
    login,
    register,
    logout,
    changePassword,
    updateUser
  } = useAuth();

  // Use auth state and functions
}
```

### Auth State

```typescript
interface AuthState {
  user: User | null;           // Current user data
  accessToken: string | null;  // JWT token
  isAuthenticated: boolean;    // Auth status
  isLoading: boolean;          // Loading state
}
```

### Auth Context Methods

1. **login(credentials)** - Authenticate user
2. **register(credentials)** - Create new account
3. **logout()** - Clear authentication
4. **changePassword(passwords)** - Update password
5. **updateUser(user)** - Update user data

---

## Protected Routes

**Location:** `src/components/ProtectedRoute.tsx`

Wrap routes that require authentication:

```typescript
<Route 
  path="/protected" 
  element={
    <ProtectedRoute>
      <YourComponent />
    </ProtectedRoute>
  } 
/>
```

**Behavior:**
- Shows loading spinner while checking authentication
- Redirects to `/login` if not authenticated
- Preserves intended destination for post-login redirect

---

## Application Routes

| Route | Component | Protected | Description |
|-------|-----------|-----------|-------------|
| `/` | WelcomeRoutePage | No | Home/landing page |
| `/login` | LoginPage | No | User login |
| `/register` | RegisterPage | No | User registration |
| `/dashboard` | DashboardRoutePage | Yes | Main dashboard |
| `/chat` | ChatPage | Yes | Chat interface |
| `/uploaded-data` | UploadedDataPage | Yes | Data management |
| `/change-password` | ChangePasswordPage | Yes | Password management |

---

## Theme & Styling

All authentication pages use a consistent design system:

### Color Scheme
- **Primary:** Blue (#3B82F6) / Indigo (#4F46E5)
- **Success:** Green (#22C55E) / Emerald (#10B981)
- **Error:** Red (#EF4444)
- **Background:** Gradient backgrounds for visual appeal

### Component Design
- **Cards:** Rounded corners (16px) with shadow
- **Buttons:** Gradient with hover effects
- **Icons:** Lucide React icons for consistency
- **Typography:** Clear hierarchy with bold headers
- **Spacing:** Generous padding and margins

### Responsive Features
- Mobile-first design
- Touch-friendly input fields
- Adaptive layout for all screen sizes
- Clear error messaging

---

## Backend API Endpoints

### Required Endpoints

Your backend API must implement these endpoints:

#### POST `/api/v1/auth/register`
```json
Request:
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "confirm_password": "password123"
}

Response (201):
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "created_at": "2026-01-13T14:30:00"
  }
}
```

#### POST `/api/v1/auth/login`
```json
Request:
{
  "identifier": "user@example.com",
  "password": "password123"
}

Response (200):
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username"
  }
}
```

#### GET `/api/v1/auth/me`
```
Headers: Authorization: Bearer {token}

Response (200):
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "created_at": "2026-01-13T14:30:00",
  "updated_at": "2026-01-13T14:30:00"
}
```

#### POST `/api/v1/auth/change-password`
```json
Request:
Headers: Authorization: Bearer {token}

{
  "current_password": "oldpass",
  "new_password": "newpass123",
  "confirm_password": "newpass123"
}

Response (200):
{
  "success": true,
  "message": "Password changed successfully"
}
```

#### POST `/api/v1/auth/verify-token`
```
Headers: Authorization: Bearer {token}

Response (200):
{
  "success": true,
  "message": "Token is valid",
  "data": {
    "user_id": 1,
    "email": "user@example.com",
    "username": "username"
  }
}
```

#### POST `/api/v1/auth/logout`
```
Headers: Authorization: Bearer {token}

Response (200):
{
  "success": true,
  "message": "Logout successful"
}
```

---

## Usage Examples

### Example 1: Login Flow
```typescript
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

function LoginForm() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (email: string, password: string) => {
    try {
      await login({ identifier: email, password });
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    // Form JSX
  );
}
```

### Example 2: Protected Component
```typescript
import { useAuth } from '../context/AuthContext';

function Dashboard() {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <div>Not authenticated</div>;
  }

  return (
    <div>
      <h1>Welcome, {user?.username}!</h1>
    </div>
  );
}
```

### Example 3: Making Authenticated API Calls
```typescript
import { getAuthHeader } from '../services/api';

async function fetchUserData() {
  const response = await fetch('/api/user/data', {
    headers: {
      ...getAuthHeader(),
      'Content-Type': 'application/json'
    }
  });

  return response.json();
}
```

---

## Security Best Practices

1. **HTTPS Only** - Always use HTTPS in production
2. **Token Storage** - Tokens stored in localStorage (consider httpOnly cookies for production)
3. **Password Requirements** - Enforce strong passwords (8+ characters)
4. **CORS** - Properly configure backend CORS
5. **Token Refresh** - Implement token refresh for long sessions
6. **Input Validation** - Validate all inputs before sending
7. **Error Handling** - Don't expose sensitive information in errors

---

## Troubleshooting

### "Authentication required" redirect
- Ensure token is stored in localStorage
- Check if `isAuthenticated()` returns true
- Verify token hasn't expired

### "Invalid credentials" error
- Verify email/username is correct
- Check password is entered correctly
- Ensure backend API is running

### Token not persisting
- Check browser localStorage settings
- Verify token is being set with `setAuthToken()`
- Check for browser privacy/incognito mode

### CORS errors
- Configure backend CORS headers
- Check API URL in `.env`
- Verify request headers are correct

---

## Environment Configuration

Create a `.env` file in project root:

```
VITE_API_URL=http://localhost:8000
VITE_CSV_API_URL=http://localhost:8001
```

---

## File Structure

```
src/
├── pages/
│   ├── LoginPage.tsx          # Login form
│   ├── RegisterPage.tsx       # Registration form
│   └── ChangePasswordPage.tsx # Password change form
├── context/
│   └── AuthContext.tsx        # Auth state management
├── components/
│   └── ProtectedRoute.tsx     # Route protection
├── services/
│   └── api.ts                 # API functions
├── types/
│   └── index.ts               # Type definitions
└── App.tsx                    # Route configuration
```

---

## Next Steps

1. **Backend Setup** - Implement auth endpoints as documented
2. **Database** - Create users table with proper schema
3. **Testing** - Test all auth flows in Postman/browser
4. **Token Refresh** - Add refresh token mechanism
5. **Error Handling** - Implement error boundary
6. **Logging** - Add audit logging for security
7. **2FA** - Consider implementing two-factor authentication

---

## Support & Maintenance

For updates to the authentication system:
1. Update types in `src/types/index.ts`
2. Update API functions in `src/services/api.ts`
3. Update context in `src/context/AuthContext.tsx`
4. Update pages as needed
5. Test all flows before deployment

---

**Last Updated:** January 13, 2026
**Version:** 1.0
