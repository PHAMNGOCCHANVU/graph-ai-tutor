"use client";

/**
 * Vietnamese error messages for API responses
 * Maps error codes/status to user-friendly Vietnamese messages
 */
export const ERROR_MESSAGES: Record<number | string, string> = {
  // Authentication Errors
  401: "Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.",
  403: "Bạn không có quyền truy cập tài nguyên này.",
  
  // Validation Errors
  400: "Dữ liệu không hợp lệ. Vui lòng kiểm tra lại.",
  422: "Dữ liệu gửi lên không đúng định dạng.",
  
  // Not Found
  404: "Tài nguyên không tồn tại.",
  
  // Server Errors
  500: "Lỗi máy chủ. Vui lòng thử lại sau.",
  502: "Lỗi cổng. Máy chủ không phản hồi.",
  503: "Dịch vụ tạm thời không khả dụng.",
  
  // Network Errors
  NETWORK_ERROR: "Lỗi kết nối. Vui lòng kiểm tra kết nối internet.",
  TIMEOUT: "Yêu cầu hết thời gian. Vui lòng thử lại.",
  UNKNOWN_ERROR: "Lỗi không xác định. Vui lòng thử lại.",
  
  // Auth Specific
  INVALID_CREDENTIALS: "Email hoặc mật khẩu không đúng.",
  EMAIL_EXISTS: "Email này đã được đăng ký.",
  USERNAME_EXISTS: "Tên người dùng này đã tồn tại.",
  USER_NOT_FOUND: "Người dùng không tồn tại.",
  
  // Token Errors
  INVALID_TOKEN: "Token không hợp lệ.",
  EXPIRED_TOKEN: "Token hết hạn.",
  NO_TOKEN: "Không tìm thấy token xác thực.",
  REFRESH_FAILED: "Không thể làm mới token. Vui lòng đăng nhập lại.",
};

/**
 * Get user-friendly error message from status code or error type
 */
export function getErrorMessage(errorOrStatus: number | string | unknown): string {
  // If it's a number (status code)
  if (typeof errorOrStatus === 'number') {
    return ERROR_MESSAGES[errorOrStatus] || ERROR_MESSAGES.UNKNOWN_ERROR;
  }

  // If it's a string
  if (typeof errorOrStatus === 'string') {
    return ERROR_MESSAGES[errorOrStatus] || errorOrStatus;
  }

  // If it's an error object
  if (errorOrStatus instanceof Error) {
    // Check if error message is in our translations
    if (ERROR_MESSAGES[errorOrStatus.message]) {
      return ERROR_MESSAGES[errorOrStatus.message];
    }
    return errorOrStatus.message || ERROR_MESSAGES.UNKNOWN_ERROR;
  }

  // If it's an axios error
  if (
    errorOrStatus &&
    typeof errorOrStatus === 'object' &&
    'response' in errorOrStatus
  ) {
    const error = errorOrStatus as any;
    const status = error.response?.status;
    const detail = error.response?.data?.detail;

    if (detail) {
      // Try to map detail to Vietnamese if it's a known error
      if (detail.includes('not found')) {
        return ERROR_MESSAGES[404];
      }
      if (detail.includes('invalid')) {
        return ERROR_MESSAGES.INVALID_CREDENTIALS;
      }
      return detail;
    }

    if (status) {
      return ERROR_MESSAGES[status] || ERROR_MESSAGES.UNKNOWN_ERROR;
    }
  }

  return ERROR_MESSAGES.UNKNOWN_ERROR;
}

/**
 * Check if error is recoverable
 */
export function isRecoverableError(status?: number): boolean {
  return ![401, 403, 404, 422].includes(status || 0);
}

/**
 * Check if error is an authentication error
 */
export function isAuthError(status?: number): boolean {
  return status === 401 || status === 403;
}

/**
 * Check if error is a network error
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof Error) {
    return (
      error.message === 'Network Error' ||
      error.message.includes('ECONNREFUSED') ||
      error.message.includes('ENOTFOUND')
    );
  }
  return false;
}

/**
 * Log error for debugging (only in development)
 */
export function logError(
  context: string,
  error: unknown,
  additionalInfo?: Record<string, unknown>
): void {
  if (process.env.NODE_ENV === 'development') {
    console.error(`[${context}]`, error, additionalInfo);
  }
}
