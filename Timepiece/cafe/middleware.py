from django.urls import resolve
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.deprecation import MiddlewareMixin
from django_otp import user_has_device
from django_otp.util import is_verified
from .auth import log_security_event, get_client_ip
import logging
import time
import re

# Security logger for middleware events - implements security monitoring requirement
security_logger = logging.getLogger('security')

# URLs exempt from two-factor authentication - balance security with usability
OTP_EXEMPT_URLS = [
    r'^/login/',
    r'^/two_factor/setup/',
    r'^/static/',
    r'^/media/',
    r'^/api/',
]

class SecurityMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        # Initialize request timing for performance monitoring
        request.start_time = time.time()
        
        # Check for potentially malicious inputs - implements attack prevention requirement
        self._check_for_suspicious_patterns(request)
        
        # Enforce two-factor authentication if required - implements enhanced authentication requirement
        if self._should_enforce_2fa(request):
            return redirect(settings.LOGIN_URL)
    
    def process_response(self, request, response):
        # Performance monitoring - identify abnormally slow requests that could indicate DoS attacks
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            if duration > 3.0:
                security_logger.warning(
                    f"Slow request detected: {request.method} {request.path} - "
                    f"Duration: {duration:.2f}s, IP: {get_client_ip(request)}"
                )
        
        # Apply security headers to all responses - implements secure communication requirement
        self._ensure_security_headers(response)
        
        return response
    
    def _check_for_suspicious_patterns(self, request):
        # Analyze query string for potential SQL injection patterns - attack prevention requirement
        query_string = request.META.get('QUERY_STRING', '')
        
        # SQL injection pattern detection - defense against database attacks
        sql_patterns = [
            r'(\%27)|(\')|(\-\-)|(\%23)|(#)',
            r'((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))',
            r'((\%27)|(\'))union',
            r'exec(\s|\+)+(s|x)p\w+',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, query_string, re.IGNORECASE):
                security_logger.warning(
                    f"Potential SQL Injection detected: {query_string} - "
                    f"IP: {get_client_ip(request)}, Path: {request.path}"
                )
                break
        
        # XSS (Cross-Site Scripting) detection - client-side attack prevention
        xss_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onload=',
            r'eval\(',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, query_string, re.IGNORECASE):
                security_logger.warning(
                    f"Potential XSS attempt detected: {query_string} - "
                    f"IP: {get_client_ip(request)}, Path: {request.path}"
                )
                break
    
    def _should_enforce_2fa(self, request):
        # Determine if two-factor authentication should be enforced for this request
        # Part of the enhanced security requirement for sensitive operations
        if not request.user.is_authenticated:
            return False
        
        # Skip 2FA for exempted URLs (public or setup paths)
        for url_pattern in OTP_EXEMPT_URLS:
            if re.match(url_pattern, request.path):
                return False
        
        # If user has 2FA device but not verified for this session, enforce verification
        if user_has_device(request.user) and not is_verified(request.user):
            return True
        
        return False
    
    def _ensure_security_headers(self, response):
        # Apply Content Security Policy - prevents XSS by controlling resource loading
        if 'Content-Security-Policy' not in response:
            response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
        
        # Prevent MIME type sniffing - protects against MIME confusion attacks
        if 'X-Content-Type-Options' not in response:
            response['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking by controlling iframe usage
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Force HTTPS connections in production - implements secure transport requirement
        if 'Strict-Transport-Security' not in response and not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response