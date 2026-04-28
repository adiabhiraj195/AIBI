# Authentication Implementation

## Overview
This project now includes a complete authentication system with JWT token-based authentication. Users can log in using their email or username and receive an access token for API authentication.

## Components

### 1. Authentication Types (`src/types/index.ts`)
- **User**: User profile information
- **LoginRequest**: Login credentials (email/username)
- **LoginResponse**: Response containing access token and user data
- **AuthState**: Application authentication state

### 2. Authentication API (`src/services/api.ts`)
- `login(credentials)`: Authenticate user and get access token
- `logout()`: Clear stored credentials
- `getAuthToken()`: Retrieve stored token
- `setAuthToken(token)`: Store authentication token
- `getAuthUser()`: Retrieve stored user data
- `setAuthUser(user)`: Store user information
- `isAuthenticated()`: Check authentication status
- `getAuthHeader()`: Get authorization header for API requests

### 3. Auth Context (`src/context/AuthContext.tsx`)
Provides global authentication state management using React Context:
- Automatically loads stored authentication on app start
- Manages login/logout operations
- Provides authentication state to all components

### 4. Login Page (`src/pages/LoginPage.tsx`)
User-friendly login interface with:
- Email or username input
- Optional password field
- Error handling and loading states
- Automatic redirect to dashboard after successful login

### 5. Protected Route (`src/components/ProtectedRoute.tsx`)
Component to protect routes that require authentication:
- Shows loading state while checking authentication
- Redirects to login page if user is not authenticated
- Preserves the intended destination for post-login redirect

## Usage

### Accessing the Login Page
Navigate to `/login` in your application.

### Protecting Routes
To protect a route, wrap it with the `ProtectedRoute` component in `App.tsx`:

```tsx
import ProtectedRoute from './components/ProtectedRoute';

<Route 
  path="/dashboard" 
  element={
    <ProtectedRoute>
      <DashboardRoutePage />
    </ProtectedRoute>
  } 
/>
```

### Using Authentication in Components
Access authentication state and functions using the `useAuth` hook:

```tsx
import { useAuth } from '../context/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();
  
  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }
  
  return (
    <div>
      <h1>Welcome, {user?.username}!</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Making Authenticated API Requests
Add the authorization header to your API requests:

```tsx
import { getAuthHeader } from '../services/api';

fetch('http://api.example.com/data', {
  headers: {
    ...getAuthHeader(),
    'Content-Type': 'application/json'
  }
});
```

## Backend Requirements

Your backend API should implement the following endpoint:

### POST `/api/v1/auth/login`

**Request Body:**
```json
{
  "identifier": "user@example.com",  // or username
  "password": "optional_password"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user123",
    "username": "johndoe",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "admin"
  },
  "expires_in": 3600
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid credentials"
}
```

## Security Notes

1. **Token Storage**: Tokens are stored in localStorage for persistence across sessions
2. **HTTPS**: In production, always use HTTPS to protect tokens in transit
3. **Token Expiration**: Implement token refresh mechanism for long-lived sessions
4. **CORS**: Ensure your backend API properly configures CORS headers
5. **Password**: The password field is optional in the current implementation - adjust based on your security requirements

## Next Steps

To fully integrate authentication:

1. Update your backend to implement the `/api/v1/auth/login` endpoint
2. Protect sensitive routes using `ProtectedRoute`
3. Add token refresh logic for expired tokens
4. Implement additional auth features (registration, password reset, etc.)
5. Add logout button to navigation/header components
6. Update API calls to include authentication headers where needed

## Environment Variables

Configure the API URL in your `.env` file:

```
VITE_API_URL=http://localhost:8000
```

## Testing

1. Start your backend server
2. Navigate to `/login`
3. Enter your credentials
4. Verify successful redirect to dashboard
5. Check localStorage for stored token and user data
6. Test protected routes without authentication
7. Test logout functionality
