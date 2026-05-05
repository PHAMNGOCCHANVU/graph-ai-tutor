import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Protected routes that require authentication
const protectedRoutes = [
  '/algorithm',
];

// Public routes (accessible without auth)
const publicRoutes = [
  '/login',
  '/signup',
  '/',
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Get token from cookies (for future use when we implement cookie storage)
  const token = request.cookies.get('accessToken')?.value;

  // Check if route is protected
  const isProtectedRoute = protectedRoutes.some((route) => pathname.startsWith(route));
  const isPublicRoute = publicRoutes.includes(pathname);

  // If accessing protected route without token, redirect to login
  if (isProtectedRoute && !token) {
    // Note: This check works only for cookie-based tokens
    // Client-side localStorage check is handled in components
    // This middleware is here for defense-in-depth
    return NextResponse.next();
  }

  // If logged in and accessing login/signup, allow (client-side redirect can happen)
  if (token && (pathname === '/login' || pathname === '/signup')) {
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
