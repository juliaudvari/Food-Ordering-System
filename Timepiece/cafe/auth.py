from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
import logging

# Security logger for audit trail - implements security monitoring requirement
security_logger = logging.getLogger('security')

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # Track successful logins for security audit - part of security monitoring requirement
    ip_address = get_client_ip(request)
    security_logger.info(
        f"Login successful - Username: {user.username}, IP: {ip_address}, "
        f"User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
    )
    
    # Update last login timestamp for user activity tracking
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    # Track user logouts for security audit - maintains session integrity
    if user:
        ip_address = get_client_ip(request)
        security_logger.info(
            f"User logged out - Username: {user.username}, IP: {ip_address}, "
            f"User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
        )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    # Log failed login attempts - critical for detecting brute force attacks
    # Addresses security requirement for intrusion detection
    ip_address = get_client_ip(request)
    username = credentials.get('username', 'unknown')
    security_logger.warning(
        f"Login failed - Username: {username}, IP: {ip_address}, "
        f"User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
    )

def get_client_ip(request):
    # Utility function to extract client IP, handling proxy scenarios
    # Important for accurate security logging and potential IP blocking
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip

def log_security_event(request, event_type, message, level='info'):
    # Generic security event logger with severity levels
    # Provides comprehensive audit trail for security-related events
    ip_address = get_client_ip(request)
    user = request.user.username if request.user.is_authenticated else 'anonymous'
    
    log_message = (
        f"[{event_type}] {message} - User: {user}, IP: {ip_address}, "
        f"User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
    )
    
    if level == 'warning':
        security_logger.warning(log_message)
    elif level == 'error':
        security_logger.error(log_message)
    elif level == 'critical':
        security_logger.critical(log_message)
    else:
        security_logger.info(log_message)

def log_otp_event(request, event, device=None):
    # Two-factor authentication logging - implements enhanced security requirement
    # Tracks OTP usage for security verification
    event_type = "2FA"
    user = request.user.username if request.user.is_authenticated else 'anonymous'
    device_name = device.__class__.__name__ if device else 'None'
    
    message = f"{event} - Device: {device_name}"
    log_security_event(request, event_type, message)

def log_failed_verification(request, device=None):
    # Failed 2FA verification logging - critical security monitoring
    # Key component of intrusion detection for authorized accounts
    event_type = "2FA"
    user = request.user.username if request.user.is_authenticated else 'anonymous'
    device_name = device.__class__.__name__ if device else 'None'
    
    message = f"Failed verification - Device: {device_name}"
    log_security_event(request, event_type, message, level='warning')