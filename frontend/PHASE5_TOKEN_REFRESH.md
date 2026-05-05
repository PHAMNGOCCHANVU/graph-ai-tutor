# PHASE 5: Token Refresh & Advanced Error Handling

## Overview
Phase 5 implements comprehensive error handling, automatic token refresh with retry logic, and session timeout management. The system now gracefully handles network failures, token expiration, and provides user-friendly Vietnamese error messages.

## Features Implemented

### 1. Error Handling Utilities
**File**: `frontend/src/utils/errorHandler.ts`

- **Vietnamese Error Messages**: Maps HTTP status codes to user-friendly Vietnamese messages
- **Error Classification**: Functions to identify auth errors, network errors, recoverable errors
- **Development Logging**: Console logging in development mode for debugging

**Error Messages Map**:
```typescript
401 → "Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại."
403 → "Bạn không có quyền truy cập tài nguyên này."
404 → "Tài nguyên không tồn tại."
500 → "Lỗi máy chủ. Vui lòng thử lại sau."
NETWORK_ERROR → "Lỗi kết nối. Vui lòng kiểm tra kết nối internet."
INVALID_CREDENTIALS → "Email hoặc mật khẩu không đúng."
```

### 2. Token Refresh Service
**File**: `frontend/src/utils/tokenRefresh.ts`

- **Retry Logic**: Automatically retries failed refresh attempts (up to 3 times)
- **Exponential Backoff**: Delays between retries using exponential backoff
- **JWT Decoding**: Decodes JWT without verification to check expiration
- **Token Expiration Check**: Detects when token will expire soon
- **Auto-Refresh Setup**: Periodically checks and refreshes expiring tokens

**Features**:
```typescript
// Refresh with retry logic
refreshTokenWithRetry(refreshToken: string) → RefreshTokenResponse | null

// Check if token expires soon (within 5 minutes)
isTokenExpiringSoon(expiresAt: number, withinMinutes: number) → boolean

// Get token expiration from JWT
getTokenExpiration(token: string) → number | null

// Setup auto-refresh every 1 minute
setupAutoRefresh() → () => void
```

### 3. Session Timeout Management
**File**: `frontend/src/utils/sessionTimeout.ts`

- **Inactivity Tracking**: Monitors user activity (mouse, keyboard, scroll, touch)
- **Auto-Logout**: Logs out user after 30 minutes of inactivity
- **Activity Reset**: Resets timeout on user interaction
- **Remaining Time Calculation**: Shows how much time is left before timeout

**Features**:
```typescript
new SessionTimeout(timeoutMs, onTimeout)
  .start() → void
  .stop() → void
  .getTimeRemaining() → number (milliseconds)
  .resetActivity() → void
```

### 4. Enhanced API Interceptor
**File**: `frontend/src/services/api.ts` (Updated)

**Improvements**:
- Uses `refreshTokenWithRetry()` for intelligent token refresh
- Better error logging with context information
- Attaches user-friendly error messages to error objects
- Logs endpoint, method, status for debugging
- Handles network errors gracefully

**Flow**:
```
API Request
    ↓
Add Authorization header (from store)
    ↓
Send request
    ↓
Success? → Return response
    ↓
401 Response?
    ↓
Has refresh token? → Try refreshTokenWithRetry()
    ↓
Success? → Update store, retry original request
    ↓
Failed? → Logout and redirect to /login
    ↓
Attach user message to error → Reject
```

### 5. Error Boundary Component
**File**: `frontend/src/components/ErrorBoundary.tsx`

- **Catches React Errors**: Prevents white screen of death
- **User-Friendly Display**: Shows lock icon and Vietnamese error message
- **Reload Option**: Button to reload page
- **Development Mode**: Shows error stack trace in development

### 6. Enhanced RootProvider
**File**: `frontend/src/components/RootProvider.tsx` (Updated)

**New Features**:
- Loads auth state on app startup
- Sets up auto-refresh for tokens (checks every 1 minute)
- Starts session timeout (30 minutes inactivity)
- Cleans up intervals on logout
- Prevents memory leaks with proper cleanup

**Lifecycle**:
```
App Start
  ↓
Load auth from localStorage
  ↓
If authenticated:
  → Start auto-refresh (1 min interval)
  → Start session timeout (30 min)
  ↓
If not authenticated:
  → Stop auto-refresh
  → Stop session timeout
  ↓
On unmount:
  → Cleanup all intervals
```

## User Experience Flows

### Scenario 1: Token Expires During Use
```
User actively using app
  ↓
Token approaching expiration (within 5 minutes)
  ↓
Auto-refresh runs automatically
  ↓
Token refreshed silently (no user interaction)
  ↓
User continues using app seamlessly
```

### Scenario 2: Session Times Out
```
User stops interacting with app
  ↓
30 minutes pass without activity
  ↓
Session automatically logs out
  ↓
User redirected to /login
  ↓
Message: "Phiên đăng nhập hết hạn"
```

### Scenario 3: Network Error During Request
```
User makes API request
  ↓
Network error occurs
  ↓
Interceptor detects error
  ↓
User-friendly message attached: "Lỗi kết nối..."
  ↓
Component displays error message
```

### Scenario 4: API Server Error
```
User makes API request
  ↓
Server returns 500 error
  ↓
Interceptor logs: { status: 500, endpoint: "/api/v1/init", method: "POST" }
  ↓
Error message: "Lỗi máy chủ. Vui lòng thử lại sau."
  ↓
Developer can check console logs in development
```

## Vietnamese Error Messages

| Situation | Message |
|-----------|---------|
| Token expired (401) | "Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại." |
| Access forbidden (403) | "Bạn không có quyền truy cập tài nguyên này." |
| Not found (404) | "Tài nguyên không tồn tại." |
| Bad request (400) | "Dữ liệu không hợp lệ. Vui lòng kiểm tra lại." |
| Server error (500) | "Lỗi máy chủ. Vui lòng thử lại sau." |
| Network error | "Lỗi kết nối. Vui lòng kiểm tra kết nối internet." |
| Timeout | "Yêu cầu hết thời gian. Vui lòng thử lại." |
| Invalid credentials | "Email hoặc mật khẩu không đúng." |
| Email exists | "Email này đã được đăng ký." |
| Session timeout | "Phiên làm việc hết hạn vì không hoạt động." |

## Technical Architecture

### Auto-Refresh Flow
```
┌─────────────────────────────────────────────┐
│ Every 1 minute (setupAutoRefresh)           │
└──────────────────┬──────────────────────────┘
                   ↓
        Check if token expires within 5 min
                   ↓
         Token expiring soon detected?
                   ↓
              YES → Attempt refresh
                   ↓
         refreshTokenWithRetry(refreshToken)
                   ↓
              ┌────┴────┐
              ↓         ↓
          SUCCESS    FAIL
              ↓         ↓
         Update    Logout +
         Token     Redirect
                   to /login
```

### Error Handling Chain
```
┌──────────────────────────────┐
│ API Request                  │
└─────────────┬────────────────┘
              ↓
    ┌─────────────────────────┐
    │ Request Interceptor     │
    │ Add Bearer Token        │
    └────────────┬────────────┘
                 ↓
    ┌─────────────────────────────────────────┐
    │ Response Interceptor                    │
    │ Check Status                            │
    └──────────┬──────────────────────────────┘
               ↓
    ┌──────────┴──────────────┐
    ↓                        ↓
  200-399              4xx/5xx
    ↓                        ↓
 SUCCESS            Handle Error
    ↓                        ↓
 Return           Is 401 & has
Response          refresh token?
    ↓                        ↓
 Done              ┌─────┴─────┐
                   ↓           ↓
                 YES          NO
                   ↓           ↓
              Retry        Logout
              Logic        Redirect
```

## Browser Developer Tools

### Check Auto-Refresh in Action
```javascript
// Open DevTools → Console
// Watch for:
// [Auto Refresh] Token expiring soon, attempting refresh...
// [Auto Refresh] Token refreshed successfully

// Check token in localStorage:
JSON.parse(localStorage.getItem("user-store"))?.state?.accessToken
```

### Check Session Timeout
```javascript
// Session timeout triggers after 30 minutes of inactivity
// Activity detected on:
// - Mouse movement
// - Keyboard input
// - Scrolling
// - Touch events
// - Clicks

// To test manually:
// 1. Set timeout to 1 minute in code
// 2. Don't interact for 1 minute
// 3. Should auto-logout
```

## Configuration

All timeouts are configurable in the code:

```typescript
// Auto-refresh setup (RootProvider.tsx)
setupAutoRefresh() // Checks every 1 minute
setupAutoRefresh() // Refreshes if token expires within 5 minutes

// Session timeout (RootProvider.tsx)
30 * 60 * 1000 // 30 minutes

// Token refresh retry (tokenRefresh.ts)
MAX_REFRESH_ATTEMPTS = 3 // Max 3 retry attempts
REFRESH_RETRY_DELAY_MS = 1000 // Start with 1 second delay
```

## Testing Checklist

### Token Refresh
- [ ] Let app idle for 20+ minutes (token approaching expiration)
- [ ] Open console and watch for refresh logs
- [ ] Token should refresh automatically
- [ ] Continue using app without interruption

### Session Timeout
- [ ] Modify timeout to 2 minutes in code
- [ ] Login and don't interact
- [ ] After 2 minutes → auto-logout
- [ ] Verify redirected to /login

### Error Handling
- [ ] Disconnect internet → make API request → see "Lỗi kết nối"
- [ ] Try invalid login → see "Email hoặc mật khẩu không đúng"
- [ ] Try registered email → see "Email này đã được đăng ký"
- [ ] Access algorithm without auth → see lock + "Đăng nhập"

### Error Boundary
- [ ] Manually throw error in component
- [ ] See error boundary display error
- [ ] Click "Tải lại trang" → reloads app

## Files Created/Updated Summary

```
✅ frontend/src/utils/errorHandler.ts (NEW)
   └─ Vietnamese error messages mapping
   └─ Error classification utilities

✅ frontend/src/utils/tokenRefresh.ts (NEW)
   └─ Token refresh with retry logic
   └─ JWT token expiration checking
   └─ Auto-refresh setup

✅ frontend/src/utils/sessionTimeout.ts (NEW)
   └─ Inactivity tracking
   └─ Auto-logout on timeout
   └─ Activity reset on user interaction

✅ frontend/src/services/api.ts (UPDATED)
   └─ Enhanced error handling
   └─ Better logging
   └─ Uses new tokenRefresh utilities

✅ frontend/src/components/ErrorBoundary.tsx (NEW)
   └─ Catches React errors
   └─ Shows user-friendly error page

✅ frontend/src/components/RootProvider.tsx (UPDATED)
   └─ Setup auto-refresh on mount
   └─ Setup session timeout on mount
   └─ Proper cleanup on logout

✅ frontend/src/app/layout.tsx (UPDATED)
   └─ Wrapped with ErrorBoundary
```

## Next Steps

Phase 5 is complete! The authentication system now includes:

✅ Automatic token refresh before expiration
✅ Session timeout with inactivity tracking
✅ Comprehensive error handling with Vietnamese messages
✅ Retry logic for network failures
✅ Error boundary for crash handling
✅ Development logging for debugging

The entire authentication flow is production-ready!

## Production Considerations

For production deployment:

1. **Store tokens in httpOnly cookies** instead of localStorage for XSS protection
2. **Implement CSRF protection** on login/logout endpoints
3. **Enable HTTPS only** for all API calls
4. **Set proper CORS headers** on backend
5. **Monitor error logs** on backend for suspicious patterns
6. **Implement rate limiting** on auth endpoints
7. **Add 2FA support** for enhanced security
8. **Use secure password hashing** (already using bcrypt with 12 rounds)
9. **Implement audit logging** for auth events
10. **Set up security monitoring** and alerts
