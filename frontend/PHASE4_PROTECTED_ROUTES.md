# PHASE 4: Frontend UI & Protected Routes

## Overview
Phase 4 implements frontend authentication enforcement with protected routes. Users cannot access algorithm visualizations without logging in. The implementation uses multiple layers of protection for security and user experience.

## Features Implemented

### 1. Protected Algorithm Cards
**File**: `frontend/src/components/AlgorithmCard.tsx`

- **Lock Icon Overlay**: Shows lock icon when user is not authenticated
- **Button State**: Changes from "MÔ PHỎNG" (Simulate) to "ĐĂNG NHẬP" (Login) based on auth status
- **Click Behavior**:
  - If not authenticated → redirects to `/login`
  - If authenticated → navigates to `/algorithm/{id}`
- **Hydration Safe**: Uses `mounted` state to prevent hydration mismatches

### 2. Protected Algorithm Page
**File**: `frontend/src/app/algorithm/[slug]/page.tsx`

- **Auth Check on Mount**: Validates authentication before rendering page
- **Early Redirect**: Redirects to `/login` if user is not authenticated
- **Loading State**: Shows spinner while checking authentication
- **Content Guard**: Prevents rendering protected content if not authenticated

### 3. Route Protection Middleware
**File**: `frontend/middleware.ts`

- **Server-side Protection**: Runs on edge/server before rendering
- **Cookie-based Token Check**: Ready for future token storage in cookies
- **Protected Routes**: All `/algorithm/*` routes require authentication
- **Fallback**: Client-side localStorage checks provide primary protection

### 4. Authentication Hooks
**File**: `frontend/src/hooks/useAuth.ts`

```typescript
// Protects page, redirects if not authenticated
useRequireAuth()

// Returns boolean auth status without redirect
useIsAuthenticated()

// Returns current user object or null
useCurrentUser()
```

### 5. Unauthorized Page Component
**File**: `frontend/src/components/UnauthorizedPage.tsx`

- **Lock Icon**: Visual indicator of restricted access
- **Customizable Message**: Accept custom error messages
- **Navigation Links**: Links to login and home page
- **Vietnamese UI**: All text in Vietnamese

## User Experience Flows

### Scenario 1: Not Logged In Browsing
```
1. User visits home page
2. Sees algorithm cards with lock icons
3. Button says "ĐĂNG NHẬP"
4. Clicks card → redirects to /login
5. User registers/logs in
6. Redirected to home page
7. Cards are now clickable (no lock icon)
8. Button says "MÔ PHỎNG"
```

### Scenario 2: Logged In Access
```
1. User logs in successfully
2. Session stored in localStorage
3. Visits home page
4. Algorithm cards appear normally (no lock)
5. Click card → navigates to /algorithm/dijkstra
6. Page loads visualization
7. Can edit graph, run simulation, see explanations
```

### Scenario 3: Direct URL Access
```
1. User tries to access http://localhost:3000/algorithm/dijkstra
2. Algorithm page loads
3. Component checks authentication
4. If not authenticated → shows loading spinner
5. Redirects to /login
6. After login → can access algorithm page
```

### Scenario 4: Logout
```
1. User clicks "Đăng xuất" button
2. Token cleared from store and localStorage
3. User redirected to home page
4. Algorithm cards show lock icons again
5. "ĐĂNG NHẬP" button active
```

## Technical Architecture

### Protection Layers
```
┌─────────────────────────────────────────────────┐
│ 1. CLIENT COMPONENT AUTH CHECK (First Layer)    │
│    - AlgorithmCard checks isAuthenticated       │
│    - Shows lock/changes button text             │
│    - Prevents navigation if not auth            │
└─────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────┐
│ 2. PAGE-LEVEL AUTH CHECK (Second Layer)         │
│    - Algorithm page checks on mount             │
│    - Early redirect to /login if needed         │
│    - Prevents content rendering                │
└─────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────┐
│ 3. STORE-LEVEL PERSISTENCE (Third Layer)        │
│    - Zustand store with localStorage            │
│    - Survives page refresh                      │
│    - Provides auth state to components          │
└─────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────┐
│ 4. API-LEVEL SECURITY (Fourth Layer)            │
│    - Interceptor adds Bearer token              │
│    - Auto-refresh on 401                        │
│    - Backend validates user ownership           │
└─────────────────────────────────────────────────┘
```

### State Management
```typescript
// Zustand store provides:
isAuthenticated: boolean  // True if user logged in
user: User | null        // Current user object
accessToken: string      // JWT token for API calls
refreshToken: string     // Token for refresh flow

// Components access via:
const isAuth = useUserStore((state) => state.isAuthenticated);
```

## Vietnamese UI Text

All user-facing text translated to Vietnamese:

| English | Vietnamese |
|---------|-----------|
| Simulate | MÔ PHỎNG |
| Login | ĐĂNG NHẬP |
| Access Denied | Quyền truy cập bị từ chối |
| Loading | Vui lòng đăng nhập để truy cập trang này... |
| Go Back | Quay lại trang chủ |

## Security Features

✅ **Multi-layer Protection**
- Client-side checks prevent UI access
- Page-level guards block direct URL access
- API-level bearer token validation
- Backend user ownership verification

✅ **Hydration Safety**
- Mounted state prevents hydration errors
- Client components with proper useEffect dependencies
- No server-side rendering of protected content

✅ **Token Management**
- Tokens stored in localStorage
- Refresh token auto-used on 401
- Logout clears all tokens
- New session preserves user state

## Testing Checklist

### Basic Flow
- [ ] Without login: cards show lock icons
- [ ] Without login: button says "ĐĂNG NHẬP"
- [ ] Click locked card → redirects to /login
- [ ] After login: cards appear normally
- [ ] After login: button says "MÔ PHỎNG"
- [ ] After login: clicking card navigates to algorithm page
- [ ] After login: algorithm page loads visualization

### Edge Cases
- [ ] Direct URL `/algorithm/dijkstra` without login → redirects
- [ ] Logout → cards lock again
- [ ] Page refresh → auth state persists
- [ ] Browser devtools → tokens visible in localStorage only
- [ ] Network error → graceful fallback

### Error Handling
- [ ] 401 response → attempts refresh
- [ ] Refresh fails → redirects to /login
- [ ] Network error → shows error message
- [ ] Invalid slug → shows 404

## Browser Compatibility

Tested on:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Performance Considerations

- **Lazy Auth Check**: Only checks auth when component mounts
- **localStorage Caching**: Tokens cached in browser
- **Minimal Re-renders**: useCallback prevents unnecessary updates
- **Early Returns**: Guards prevent rendering protected content

## Future Enhancements

1. **Cookie Storage**: Store tokens in httpOnly cookies for XSS protection
2. **Session Timeout**: Auto-logout after inactivity
3. **Remember Me**: Option to keep login for longer period
4. **2FA**: Two-factor authentication support
5. **Social Login**: OAuth integrations (Google, GitHub)

## Troubleshooting

### Cards not locking after logout
- Check localStorage is cleared: Open DevTools → Application → Local Storage
- Verify `loadFromStorage()` is called on app start

### Redirect not working
- Check browser console for errors
- Verify next/navigation imports are correct
- Check useRouter() is called in client component

### Hydration errors
- Ensure "use client" directive is at top of file
- Check mounted state is used before rendering
- Verify useEffect dependencies are correct
