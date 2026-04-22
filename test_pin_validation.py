#!/usr/bin/env python
"""
Test script to verify PIN validation rejects weak PINs like 1234.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, 'D:\\campo')
django.setup()

from resort_portal.services import ManagerAuthService

def test_pin_validation():
    """Test PIN validation logic."""
    
    print("=== PIN VALIDATION TEST ===\n")
    
    # Test cases: (pin, should_be_valid, expected_error)
    test_cases = [
        # Valid PINs
        ("5729", True, ""),
        ("8462", True, ""),
        ("3951", True, ""),
        
        # Invalid PINs - wrong length
        ("12", False, "PIN must be exactly 4 digits"),
        ("12345", False, "PIN must be exactly 4 digits"),
        ("", False, "PIN must be exactly 4 digits"),
        
        # Invalid PINs - non-digits
        ("12ab", False, "PIN must contain only digits"),
        ("a123", False, "PIN must contain only digits"),
        ("123a", False, "PIN must contain only digits"),
        
        # Invalid PINs - weak patterns
        ("0000", False, "PIN is too common (all same digit)"),
        ("1111", False, "PIN is too common (all same digit)"),
        ("1234", False, "PIN is too common (sequential)"),
        ("4321", False, "PIN is too common (sequential)"),
        ("0123", False, "PIN is too common (sequential)"),
        ("6789", False, "PIN is too common (sequential)"),
    ]
    
    passed = 0
    failed = 0
    
    for pin, expected_valid, expected_error in test_cases:
        is_valid, error_message = ManagerAuthService.validate_pin(pin)
        
        if is_valid == expected_valid:
            if expected_valid:
                print(f"  PASS: '{pin}' correctly accepted")
            else:
                if expected_error.lower() in error_message.lower():
                    print(f"  PASS: '{pin}' correctly rejected - {error_message}")
                else:
                    print(f"  FAIL: '{pin}' rejected but wrong error: {error_message} (expected: {expected_error})")
                    failed += 1
                    continue
            passed += 1
        else:
            print(f"  FAIL: '{pin}' expected {'valid' if expected_valid else 'invalid'}, got {'valid' if is_valid else 'invalid'}")
            failed += 1
    
    print(f"\n=== RESULTS ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print("\n  ALL TESTS PASSED! PIN validation is working correctly.")
        print("  The system will reject weak PINs like 1234, 0000, etc.")
    else:
        print(f"\n  {failed} TESTS FAILED! PIN validation needs attention.")
    
    return failed == 0

if __name__ == "__main__":
    success = test_pin_validation()
    sys.exit(0 if success else 1)
