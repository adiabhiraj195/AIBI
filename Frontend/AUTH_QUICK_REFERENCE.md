# Authentication Quick Reference

## 🚀 Quick Start

### View Pages
- **Login:** Navigate to `http://localhost:5173/login`
- **Register:** Navigate to `http://localhost:5173/register`
- **Change Password:** Navigate to `http://localhost:5173/change-password` (requires login)

### Test Credentials
```
Email: test@example.com
Username: testuser
Password: testpass123
```

---

## 📌 Files at a Glance

### Pages (Components)
```
src/pages/
├── LoginPage.tsx              ← User login form
├── RegisterPage.tsx           ← User signup form
└── ChangePasswordPage.tsx     ← Password management (protected)
```

### Context & Utils
```
src/context/
└── AuthContext.tsx            ← Global auth state

src/components/
└── ProtectedRoute.tsx         ← Route protection wrapper

src/services/
└── api.ts                     ← Auth API functions (updated)
```

### Types
```
src/types/
└── index.ts                   ← Auth interfaces (updated)
```

### Root
```
src/
└── App.tsx                    ← Routes setup (updated)
```

---

## 🔑 API Functions

### In Your Components
```typescript
import { useAuth } from '../context/AuthContext';

const { 
  user,              // Current user data
  accessToken,       // JWT token
  isAuthenticated,   // Boolean
  isLoading,         // Loading state
  login,             // Function
  register,          // Function
  logout,            // Function
  changePassword     // Function
} = useAuth();
```

### Direct API Calls
```typescript
import * as api from '../services/api';

// Login
api.login({ identifier: 'user@example.com', password: 'pass' })

// Register
api.register({ 
  email: 'user@example.com',
  username: 'username',
  password: 'pass',
  confirm_password: 'pass'
})

// Change Password
api.changePassword({
  current_password: 'old',
  new_password: 'new',
  confirm_password: 'new'
})

// Get Token
api.getAuthToken()

// Get User
api.getAuthUser()

// Check Auth
api.isAuthenticated()

// Auth Header
api.getAuthHeader()

// Logout
api.logout()
```

---

## 🛡️ Protected Routes

```typescript
import ProtectedRoute from './components/ProtectedRoute';

<Route 
  path="/protected" 
  element={
    <ProtectedRoute>
      <YourComponent />
    </ProtectedRoute>
  } 
/>
```

---

## 🎨 Page Themes

| Page | Theme | Colors |
|------|-------|--------|
| Login | Blue/Indigo | #3B82F6, #4F46E5 |
| Register | Green/Emerald | #22C55E, #10B981 |
| Change Password | Blue/Indigo | #3B82F6, #4F46E5 |

---

## ✅ Form Validation Rules

### Register Form
- **Email:** Valid format required
- **Username:** 3+ characters
- **Password:** 8+ characters
- **Confirm:** Must match password

### Change Password Form
- **Current:** Required
- **New Password:** 8+ characters, different from current
- **Confirm:** Must match new password

---

## 📡 Backend API Requirements

### Required Endpoints
```
POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/auth/me
POST /api/v1/auth/change-password
POST /api/v1/auth/verify-token
POST /api/v1/auth/logout
```

### Request/Response Format
```json
// Login Request
{ "identifier": "user@example.com", "password": "pass" }

// Login Response
{
  "access_token": "token...",
  "token_type": "bearer",
  "user": { "id": "1", "email": "...", "username": "..." }
}
```

---

## 🔐 Token Management

```typescript
// Store token
setAuthToken(token);

// Get token
const token = getAuthToken();

// Add to requests
const headers = {
  ...getAuthHeader(),  // Adds Authorization header
  'Content-Type': 'application/json'
};

// Clear token
logout();
```

---

## 🎯 Common Tasks

### Login User
```typescript
const { login } = useAuth();

try {
  await login({ 
    identifier: 'user@example.com', 
    password: 'password' 
  });
  navigate('/dashboard');
} catch (error) {
  console.error(error);
}
```

### Register User
```typescript
const { register } = useAuth();

try {
  await register({
    email: 'user@example.com',
    username: 'username',
    password: 'pass123',
    confirm_password: 'pass123'
  });
  navigate('/login');
} catch (error) {
  console.error(error);
}
```

### Change Password
```typescript
const { changePassword } = useAuth();

try {
  await changePassword({
    current_password: 'old',
    new_password: 'new',
    confirm_password: 'new'
  });
} catch (error) {
  console.error(error);
}
```

### Check Authentication
```typescript
const { isAuthenticated, user } = useAuth();

if (isAuthenticated) {
  console.log(`Welcome ${user?.username}`);
}
```

### Logout
```typescript
const { logout } = useAuth();

logout();
navigate('/login');
```

---

## 🚨 Error Handling

```typescript
try {
  await login(credentials);
} catch (err) {
  // Error messages:
  // "Invalid credentials"
  // "User not found"
  // "Email already exists"
  // "Network error"
  console.error(err.message);
}
```

---

## 📋 Checklist for Setup

- [ ] Backend `/api/v1/auth/*` endpoints implemented
- [ ] Database users table created
- [ ] CORS configured in backend
- [ ] Frontend running on localhost:5173
- [ ] Backend running on localhost:8000
- [ ] Test registration flow
- [ ] Test login flow
- [ ] Test protected routes
- [ ] Test change password
- [ ] Test logout
- [ ] Test session persistence (page refresh)

---

## 🔗 Quick Links

- [Complete Guide](COMPLETE_AUTH_GUIDE.md)
- [Architecture](AUTH_ARCHITECTURE.md)
- [Implementation Summary](AUTH_IMPLEMENTATION_SUMMARY.md)
- [Backend Guide](AUTHENTICATION_GUIDE%20copy.md)

---

## 💡 Tips

- Always use `useAuth()` hook instead of direct API calls
- All errors are caught and displayed to users
- Tokens automatically stored in localStorage
- Protected routes show loading spinner while checking auth
- All pages are responsive and mobile-friendly
- Theme colors match the rest of the application

---

## 🎯 Routes

| Path | Type | Component | Auth Required |
|------|------|-----------|---|
| `/` | Public | Welcome | ❌ |
| `/login` | Public | Login | ❌ |
| `/register` | Public | Register | ❌ |
| `/dashboard` | Protected | Dashboard | ✅ |
| `/chat` | Protected | Chat | ✅ |
| `/uploaded-data` | Protected | Data | ✅ |
| `/change-password` | Protected | Password | ✅ |

---

**Ready to use!** Start by implementing the backend endpoints.
