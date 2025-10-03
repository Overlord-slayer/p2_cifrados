#!/usr/bin/env python3
"""
Quick test script to verify security fixes are working correctly.
"""

print("Testing security fixes...")
print("-" * 50)

# Test 1: Import sanitization utility
try:
    from app.utils.sanitize import sanitize_for_output
    print("✓ Sanitization utility imported successfully")
except ImportError as e:
    print(f"✗ Failed to import sanitization utility: {e}")
    exit(1)

# Test 2: Test sanitization function
test_cases = [
    ('<script>alert("XSS")</script>', '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;'),
    ('<img src=x onerror=alert(1)>', '&lt;img src=x onerror=alert(1)&gt;'),
    ('Normal text', 'Normal text'),
    ('user@example.com', 'user@example.com'),
]

all_passed = True
for input_text, expected_output in test_cases:
    result = sanitize_for_output(input_text)
    if result == expected_output:
        print(f"✓ Sanitization test passed: {input_text[:30]}...")
    else:
        print(f"✗ Sanitization test failed: {input_text}")
        print(f"  Expected: {expected_output}")
        print(f"  Got: {result}")
        all_passed = False

# Test 3: Import main app
try:
    from app.main import app
    print("✓ FastAPI app imported successfully")
except ImportError as e:
    print(f"✗ Failed to import FastAPI app: {e}")
    exit(1)

# Test 4: Import chat endpoints
try:
    from app.endpoints.chat import router
    print("✓ Chat endpoints imported successfully")
except ImportError as e:
    print(f"✗ Failed to import chat endpoints: {e}")
    exit(1)

print("-" * 50)
if all_passed:
    print("✓ All tests passed! Security fixes are working correctly.")
    exit(0)
else:
    print("✗ Some tests failed. Please review the output above.")
    exit(1)
