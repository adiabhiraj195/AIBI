# Authentication System Architecture

## Flow Diagram

### User Registration Flow
```
┌─────────────┐
│ Register    │
│ Page        │
└──────┬──────┘
       │
       ├─► Validate Form
       │   ├─ Email format
       │   ├─ Username (3+ chars)
       │   ├─ Password (8+ chars)
       │   └─ Password match
       │
       ├─► API Call (POST /api/v1/auth/register)
       │
       ├─► Success
       │   ├─ Show success screen
       │   └─ Redirect to /login (2 sec)
       │
       └─► Error
           └─ Display error message
```

### User Login Flow
```
┌──────────────┐
│ Login        │
│ Page         │
└──────┬───────┘
       │
       ├─► Validate Form
       │   ├─ Email/Username required
       │   └─ Password required
       │
       ├─► API Call (POST /api/v1/auth/login)
       │
       ├─► Success
       │   ├─ Store token in localStorage
       │   ├─ Store user in localStorage
       │   ├─ Update AuthContext
       │   └─ Redirect to /dashboard
       │
       └─► Error
           └─ Display error message
```

### Protected Route Access Flow
```
┌─────────────────┐
│ Navigate to     │
│ Protected Route │
└────────┬────────┘
         │
         ├─► ProtectedRoute Component
         │
         ├─► Check Authentication
         │   ├─ isLoading = true?
         │   │  └─ Show loading spinner
         │   │
         │   ├─ isAuthenticated = true?
         │   │  └─ Render protected component
         │   │
         │   └─ isAuthenticated = false?
         │      └─ Redirect to /login
         │
         └─► Access Granted/Denied
```

### Change Password Flow
```
┌──────────────────────┐
│ Change Password      │
│ Page (Protected)     │
└──────┬───────────────┘
       │
       ├─► Validate Form
       │   ├─ Current password required
       │   ├─ New password (8+ chars)
       │   ├─ Password match
       │   └─ Different from current
       │
       ├─► API Call (POST /api/v1/auth/change-password)
       │    Headers: Authorization: Bearer {token}
       │
       ├─► Success
       │   ├─ Show success screen
       │   └─ Redirect to /dashboard (2 sec)
       │
       └─► Error
           └─ Display error message
```

---

## Component Architecture

```
App.tsx (Root)
│
├─► AuthProvider (Context)
│   │
│   ├─► [Auth State]
│   │   ├─ user: User | null
│   │   ├─ accessToken: string | null
│   │   ├─ isAuthenticated: boolean
│   │   └─ isLoading: boolean
│   │
│   └─► [Auth Methods]
│       ├─ login()
│       ├─ register()
│       ├─ logout()
│       ├─ changePassword()
│       └─ updateUser()
│
└─► Routes
    │
    ├─► Public Routes
    │   ├─ / (WelcomeRoutePage)
    │   ├─ /login (LoginPage)
    │   └─ /register (RegisterPage)
    │
    └─► Protected Routes
        ├─ ProtectedRoute Wrapper
        │  │
        │  ├─ /dashboard (DashboardRoutePage)
        │  ├─ /chat (ChatPage)
        │  ├─ /uploaded-data (UploadedDataPage)
        │  └─ /change-password (ChangePasswordPage)
```

---

## State Management

### AuthContext State
```typescript
{
  user: {
    id: string;
    email: string;
    username: string;
    name?: string;
    role?: string;
  } | null,
  accessToken: string | null,
  isAuthenticated: boolean,
  isLoading: boolean
}
```

### LocalStorage
```javascript
// auth_token
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

// auth_user
{
  "id": "1",
  "email": "user@example.com",
  "username": "johndoe",
  "name": "John Doe"
}
```

---

## API Layers

### Frontend → Backend Communication
```
┌──────────────────────────┐
│ React Component          │
│ (LoginPage)              │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ useAuth Hook             │
│ (context/AuthContext)    │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ API Service              │
│ (services/api.ts)        │
├─ login()                 │
├─ register()              │
├─ changePassword()        │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Backend FastAPI          │
│ (/api/v1/auth/*)         │
├─ POST /register          │
├─ POST /login             │
├─ POST /change-password   │
├─ GET /me                 │
├─ POST /verify-token      │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Database                 │
│ (PostgreSQL)             │
├─ users table             │
└──────────────────────────┘
```

---

## Data Flow Sequence

### Login Sequence
```
1. User enters credentials in LoginPage
   ↓
2. Form validation checks
   ↓
3. POST /api/v1/auth/login with credentials
   ↓
4. Backend validates credentials
   ↓
5. Backend returns {token, user}
   ↓
6. Frontend stores in localStorage
   ↓
7. AuthContext updates state
   ↓
8. useAuth hook notifies all subscribers
   ↓
9. ProtectedRoute allows access
   ↓
10. Navigate to /dashboard
```

### Protected Route Access Sequence
```
1. User navigates to /dashboard
   ↓
2. ProtectedRoute component renders
   ↓
3. Check auth state:
   - getAuthToken() from localStorage
   - getAuthUser() from localStorage
   ↓
4. If loading: show spinner
   If authenticated: render component
   If not authenticated: redirect to /login
```

---

## Component Props & Interface

### ProtectedRoute Props
```typescript
interface ProtectedRouteProps {
  children: React.ReactNode;  // Component to protect
}
```

### Auth Context Interface
```typescript
interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  register: (credentials: RegisterRequest) => Promise<void>;
  logout: () => void;
  updateUser: (user: User) => void;
  changePassword: (passwords: ChangePasswordRequest) => Promise<void>;
}
```

---

## Request/Response Examples

### Login Request
```http
POST /api/v1/auth/login HTTP/1.1
Content-Type: application/json

{
  "identifier": "user@example.com",
  "password": "securepassword123"
}
```

### Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "1",
    "email": "user@example.com",
    "username": "johndoe",
    "name": "John Doe"
  }
}
```

### Protected Request
```http
GET /api/v1/auth/me HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Change Password Request
```http
POST /api/v1/auth/change-password HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "current_password": "oldpassword123",
  "new_password": "newpassword456",
  "confirm_password": "newpassword456"
}
```

---

## Error Handling Flow

```
┌──────────────────┐
│ API Request      │
└────────┬─────────┘
         │
         ├─ Success (2xx)
         │  ├─ Parse response
         │  └─ Update state
         │
         └─ Error (4xx/5xx)
            ├─ Parse error details
            ├─ Extract message
            ├─ Display to user
            └─ Log error
```

### Error Messages
- **400 Bad Request:** Validation error (sent by user)
- **401 Unauthorized:** Invalid credentials or expired token
- **409 Conflict:** Email/username already exists
- **500 Server Error:** Backend error

---

## Security Model

### Token Management
```
┌─────────────────────┐
│ Login Successful    │
└────────┬────────────┘
         │
         ├─► setAuthToken(token)
         │   └─ Stored in localStorage
         │
         ├─► getAuthHeader()
         │   └─ { Authorization: "Bearer {token}" }
         │
         ├─► getAuthToken()
         │   └─ Retrieve for requests
         │
         └─► logout()
             └─ removeItem(token)
                 removeItem(user)
```

### Protected Routes
```
Only accessible when:
✓ localStorage has valid token
✓ isAuthenticated = true
✓ AuthProvider initialized
✓ Token not expired
```

---

## File Dependencies

```
LoginPage.tsx
  ↓
  ├─ useAuth() → AuthContext.tsx
  │  └─ login() → api.ts
  │     └─ POST /api/v1/auth/login
  │
  └─ useNavigate() → React Router

RegisterPage.tsx
  ↓
  ├─ useAuth() → AuthContext.tsx
  │  └─ register() → api.ts
  │     └─ POST /api/v1/auth/register
  │
  └─ useNavigate() → React Router

ChangePasswordPage.tsx
  ↓
  ├─ ProtectedRoute
  │  └─ useAuth() → AuthContext.tsx
  │     └─ changePassword() → api.ts
  │        └─ POST /api/v1/auth/change-password
  │
  └─ useNavigate() → React Router

ProtectedRoute.tsx
  ↓
  └─ useAuth() → AuthContext.tsx
     └─ isAuthenticated, isLoading

AuthContext.tsx
  ↓
  ├─ types/index.ts (Types & Interfaces)
  └─ services/api.ts (API Functions)

App.tsx
  ↓
  ├─ AuthProvider (Context)
  ├─ Routes
  ├─ ProtectedRoute
  └─ All page components
```

---

## Theme Integration

### Color Palette
- **Login:** Blue (#3B82F6) / Indigo (#4F46E5)
- **Register:** Green (#22C55E) / Emerald (#10B981)
- **Change Password:** Blue matching dashboard
- **Backgrounds:** Gradient overlays
- **Errors:** Red (#EF4444)

### Icon Set
- **Mail Icon** - Email/username fields
- **Lock Icon** - Password fields
- **CheckCircle Icon** - Success states
- **ArrowLeft Icon** - Back navigation

### Responsive Design
- Mobile: Full width with padding
- Tablet: Centered card layout
- Desktop: Fixed width card (max-w-md)
- Touch: Large tap targets (44px minimum)

---

## Performance Considerations

### Optimization
```
✓ Lazy loading context providers
✓ Memoized auth state
✓ useCallback for functions
✓ No unnecessary re-renders
✓ localStorage caching
✓ Single source of truth (Context)
```

### Bundle Size
```
AuthContext.tsx      ~2KB
LoginPage.tsx        ~4KB
RegisterPage.tsx     ~5KB
ChangePasswordPage   ~5KB
ProtectedRoute.tsx   ~2KB
─────────────────────────
Total Auth Module:   ~18KB (minified)
```

---

This architecture ensures:
- ✅ Secure token management
- ✅ Consistent user experience
- ✅ Type-safe implementation
- ✅ Scalable structure
- ✅ Easy maintenance
- ✅ Clear data flow
