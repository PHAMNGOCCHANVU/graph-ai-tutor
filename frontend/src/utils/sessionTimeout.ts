"use client";

/**
 * Session timeout utility for auto-logout after inactivity
 * Tracks user activity and logs out after specified duration
 */

const DEFAULT_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes
const CHECK_INTERVAL_MS = 1 * 60 * 1000; // Check every 1 minute

export class SessionTimeout {
  private timeoutId: NodeJS.Timeout | null = null;
  private checkIntervalId: NodeJS.Timeout | null = null;
  private lastActivityTime: number = Date.now();
  private timeoutMs: number;
  private onTimeout: () => void;

  constructor(timeoutMs: number = DEFAULT_TIMEOUT_MS, onTimeout: () => void = () => {}) {
    this.timeoutMs = timeoutMs;
    this.onTimeout = onTimeout;
  }

  /**
   * Start tracking session
   */
  start(): void {
    if (typeof window === 'undefined') return;

    this.lastActivityTime = Date.now();

    // Setup activity listeners
    const activityEvents = [
      'mousedown',
      'keydown',
      'scroll',
      'touchstart',
      'click',
    ];

    activityEvents.forEach((event) => {
      window.addEventListener(event, this.handleActivity, { passive: true });
    });

    // Setup periodic check
    this.checkIntervalId = setInterval(() => {
      this.checkTimeout();
    }, CHECK_INTERVAL_MS);
  }

  /**
   * Stop tracking session
   */
  stop(): void {
    if (typeof window === 'undefined') return;

    const activityEvents = [
      'mousedown',
      'keydown',
      'scroll',
      'touchstart',
      'click',
    ];

    activityEvents.forEach((event) => {
      window.removeEventListener(event, this.handleActivity);
    });

    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }

    if (this.checkIntervalId) {
      clearInterval(this.checkIntervalId);
      this.checkIntervalId = null;
    }
  }

  /**
   * Handle user activity
   */
  private handleActivity = (): void => {
    this.lastActivityTime = Date.now();
  };

  /**
   * Check if session has timed out
   */
  private checkTimeout(): void {
    const now = Date.now();
    const inactiveTime = now - this.lastActivityTime;

    if (inactiveTime >= this.timeoutMs) {
      this.onTimeout();
      this.stop();
    }
  }

  /**
   * Get time remaining in milliseconds
   */
  getTimeRemaining(): number {
    const now = Date.now();
    const inactiveTime = now - this.lastActivityTime;
    const remaining = Math.max(0, this.timeoutMs - inactiveTime);
    return remaining;
  }

  /**
   * Get time remaining in minutes
   */
  getTimeRemainingMinutes(): number {
    return Math.ceil(this.getTimeRemaining() / 1000 / 60);
  }

  /**
   * Reset activity timer (useful for important actions)
   */
  resetActivity(): void {
    this.lastActivityTime = Date.now();
  }
}

/**
 * Hook to use session timeout in components
 */
export function useSessionTimeout(
  timeoutMs?: number,
  onTimeout?: () => void
) {
  if (typeof window === 'undefined') return;

  const sessionTimeout = new SessionTimeout(timeoutMs, onTimeout);

  // Start on mount
  if (typeof window !== 'undefined') {
    sessionTimeout.start();
  }

  // Cleanup on unmount
  return () => {
    sessionTimeout.stop();
  };
}
