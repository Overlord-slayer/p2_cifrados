import time
from fastapi import HTTPException, Request
from collections import defaultdict, deque
from typing import Dict, Deque
import asyncio
from threading import Lock

class RateLimiter:
    """
    Simple in-memory rate limiter for authentication endpoints
    In production, consider using Redis for distributed rate limiting
    """
    
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts: Dict[str, Deque[float]] = defaultdict(deque)
        self.lock = Lock()
    
    def is_rate_limited(self, identifier: str) -> bool:
        """
        Check if the identifier (IP + endpoint) is rate limited
        """
        current_time = time.time()
        
        with self.lock:
            # Clean old attempts outside the time window
            while (self.attempts[identifier] and 
                   current_time - self.attempts[identifier][0] > self.window_seconds):
                self.attempts[identifier].popleft()
            
            # Check if we've exceeded the limit
            if len(self.attempts[identifier]) >= self.max_attempts:
                return True
            
            # Record this attempt
            self.attempts[identifier].append(current_time)
            return False

# Global rate limiter instances
login_limiter = RateLimiter(max_attempts=5, window_seconds=900)  # 5 attempts per 15 minutes
signup_limiter = RateLimiter(max_attempts=3, window_seconds=3600)  # 3 attempts per hour

async def rate_limit_auth_endpoints(request: Request, endpoint_type: str = "login"):
    """
    Middleware function to apply rate limiting to authentication endpoints
    """
    client_ip = request.client.host if request.client else "unknown"
    identifier = f"{client_ip}:{endpoint_type}"
    
    limiter = login_limiter if endpoint_type == "login" else signup_limiter
    
    if limiter.is_rate_limited(identifier):
        raise HTTPException(
            status_code=429,
            detail="Too many attempts. Please try again later."
        )

class SecurityHeaders:
    """
    Add security headers to responses
    """
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none';"
        }

def add_security_headers(response):
    """
    Add security headers to a response
    """
    headers = SecurityHeaders.get_security_headers()
    for key, value in headers.items():
        response.headers[key] = value
    return response

# Account lockout mechanism
class AccountLockout:
    """
    Simple account lockout mechanism to prevent brute force attacks
    In production, store this in database or Redis
    """
    
    def __init__(self, max_failed_attempts: int = 5, lockout_duration: int = 1800):
        self.max_failed_attempts = max_failed_attempts
        self.lockout_duration = lockout_duration  # 30 minutes
        self.failed_attempts: Dict[str, int] = defaultdict(int)
        self.lockout_times: Dict[str, float] = {}
        self.lock = Lock()
    
    def is_account_locked(self, email: str) -> bool:
        """Check if account is currently locked"""
        with self.lock:
            if email in self.lockout_times:
                if time.time() - self.lockout_times[email] < self.lockout_duration:
                    return True
                else:
                    # Lockout expired, clear it
                    del self.lockout_times[email]
                    self.failed_attempts[email] = 0
            return False
    
    def record_failed_attempt(self, email: str):
        """Record a failed login attempt"""
        with self.lock:
            self.failed_attempts[email] += 1
            if self.failed_attempts[email] >= self.max_failed_attempts:
                self.lockout_times[email] = time.time()
    
    def record_successful_login(self, email: str):
        """Clear failed attempts on successful login"""
        with self.lock:
            self.failed_attempts[email] = 0
            if email in self.lockout_times:
                del self.lockout_times[email]

# Global account lockout instance
account_lockout = AccountLockout()
