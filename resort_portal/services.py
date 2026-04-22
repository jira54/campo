"""
Service layer for manager authentication.
Handles all business logic, validation, and state management.
"""

import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import ManagerAuth


class ManagerAuthService:
    """Main service for manager authentication operations."""
    
    # PIN Configuration
    MIN_PIN_LENGTH = 4
    WEAK_PINS = {'0000', '1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999'}
    SEQUENTIAL_PINS = {'0123', '1234', '2345', '3456', '4567', '5678', '6789', '9876', '8765', '7654', '5432', '4321', '3210'}
    
    # Attempt limits
    MAX_PASSWORD_ATTEMPTS = 5
    PASSWORD_LOCKOUT_MINUTES = 30
    MAX_PIN_ATTEMPTS = 3
    PIN_LOCKOUT_MINUTES = 15
    
    @staticmethod
    def validate_pin(pin):
        """
        Validate PIN format and strength.
        
        Args:
            pin (str): Raw PIN input
        
        Returns:
            (bool, str): (is_valid, error_message)
        """
        pin = pin.strip()
        
        # Length check
        if len(pin) != 4:
            return False, "PIN must be exactly 4 digits"
        
        # Digit check
        if not pin.isdigit():
            return False, "PIN must contain only digits"
        
        # Weak PIN check
        if pin in ManagerAuthService.WEAK_PINS:
            return False, "PIN is too common (all same digit). Choose a different combination"
        
        # Sequential PIN check
        if pin in ManagerAuthService.SEQUENTIAL_PINS:
            return False, "PIN is too common (sequential). Choose a different combination"
        
        return True, ""
    
    @staticmethod
    def validate_password(password):
        """
        Validate password using Django's validators.
        
        Args:
            password (str): Raw password input
        
        Returns:
            (bool, list): (is_valid, error_messages)
        """
        try:
            validate_password(password)
            return True, []
        except ValidationError as e:
            return False, e.messages
    
    @staticmethod
    def generate_verification_code():
        """Generate random 6-digit verification code."""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def send_verification_email(manager_auth, code):
        """
        Send verification code via email.
        
        Args:
            manager_auth (ManagerAuth): Manager instance
            code (str): Verification code
        
        Returns:
            bool: Success/failure
        """
        subject = "Verify Your Resort Manager Email"
        message = f"""
Hello,

Your email verification code is: {code}

This code will expire in 30 minutes.

If you didn't request this, please ignore this email.

Best regards,
Resort Portal Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [manager_auth.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Email send failed: {e}")
            return False
    
    @staticmethod
    def setup_manager(vendor, email, phone, password):
        """
        Create and verify a new manager.
        
        Args:
            vendor (Vendor): Vendor instance
            email (str): Manager email
            phone (str): Manager phone
            password (str): Raw password
        
        Returns:
            (bool, ManagerAuth, str): (success, manager_auth, error_message)
        """
        # Password validation
        is_valid, errors = ManagerAuthService.validate_password(password)
        if not is_valid:
            return False, None, " ".join(errors)
        
        # Check if manager already exists
        if ManagerAuth.objects.filter(email=email).exists():
            return False, None, "Email already registered"
        
        # Create manager auth
        try:
            manager_auth = ManagerAuth.objects.create(
                vendor=vendor,
                email=email,
                phone=phone
            )
            manager_auth.set_password(password)
            
            # Generate and send verification code
            code = ManagerAuthService.generate_verification_code()
            manager_auth.verification_code = code
            manager_auth.verification_sent_at = timezone.now()
            manager_auth.save()
            
            ManagerAuthService.send_verification_email(manager_auth, code)
            
            return True, manager_auth, ""
        except Exception as e:
            return False, None, str(e)
    
    @staticmethod
    def verify_email(manager_auth, code):
        """
        Verify manager email with code.
        
        Args:
            manager_auth (ManagerAuth): Manager instance
            code (str): Verification code
        
        Returns:
            (bool, str): (success, message)
        """
        if manager_auth.is_verified:
            return False, "Email already verified"
        
        if manager_auth.verification_code != code:
            return False, "Invalid verification code"
        
        # Check expiry (30 minutes)
        if timezone.now() - manager_auth.verification_sent_at > timedelta(minutes=30):
            return False, "Verification code expired"
        
        manager_auth.is_verified = True
        manager_auth.verified_at = timezone.now()
        manager_auth.verification_code = ""
        manager_auth.save()
        
        return True, "Email verified successfully"
    
    @staticmethod
    def authenticate_password(manager_auth, password):
        """
        Authenticate manager with password.
        
        Args:
            manager_auth (ManagerAuth): Manager instance
            password (str): Raw password
        
        Returns:
            (bool, str): (success, message)
        """
        # Check lockout
        if manager_auth.is_password_locked():
            remaining_seconds = (
                manager_auth.password_locked_until - timezone.now()
            ).total_seconds()
            minutes = int(remaining_seconds / 60) + 1
            return False, f"Account locked. Try again in {minutes} minutes"
        
        # Check password
        if not manager_auth.check_password(password):
            manager_auth.record_failed_password_attempt()
            remaining = manager_auth.get_password_attempts_remaining()
            return False, f"Invalid password ({remaining} attempts remaining)"
        
        # Success
        manager_auth.reset_password_attempts()
        return True, "Password authenticated"
    
    @staticmethod
    def set_pin(manager_auth, pin, confirm_pin):
        """
        Set or update manager PIN.
        
        Args:
            manager_auth (ManagerAuth): Manager instance
            pin (str): Raw PIN
            confirm_pin (str): Confirmation PIN
        
        Returns:
            (bool, str): (success, message)
        """
        # Match check
        if pin != confirm_pin:
            return False, "PINs do not match"
        
        # Validation
        is_valid, error = ManagerAuthService.validate_pin(pin)
        if not is_valid:
            return False, error
        
        # Set PIN
        manager_auth.set_pin(pin)
        return True, "PIN updated successfully"
    
    @staticmethod
    def authenticate_pin(manager_auth, pin):
        """
        Authenticate with PIN.
        
        Args:
            manager_auth (ManagerAuth): Manager instance
            pin (str): Raw PIN
        
        Returns:
            (bool, str): (success, message)
        """
        # Check if PIN is set
        if not manager_auth.has_pin():
            return False, "PIN not configured"
        
        # Check lockout
        if manager_auth.is_pin_locked():
            remaining_seconds = (
                manager_auth.pin_locked_until - timezone.now()
            ).total_seconds()
            minutes = int(remaining_seconds / 60) + 1
            return False, f"Too many failed attempts. Try again in {minutes} minutes"
        
        # Check PIN
        if not manager_auth.check_pin(pin):
            manager_auth.record_failed_pin_attempt()
            remaining = manager_auth.get_pin_attempts_remaining()
            return False, f"Invalid PIN ({remaining} attempts remaining)"
        
        # Success
        manager_auth.reset_pin_attempts()
        return True, "PIN verified"
