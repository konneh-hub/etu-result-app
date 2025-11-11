"""
Test script to verify form validation works correctly.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ETU_Ruslts.settings')
django.setup()

from eturesultapp.forms import StudentRegistrationForm

# Test 1: Try duplicate student_id
print("=" * 60)
print("Test 1: Duplicate student_id (should fail)")
print("=" * 60)
form_data = {
    'username': 'test_student',
    'student_id': 'STU100',  # Already exists (Demo Student)
    'first_name': 'Test',
    'last_name': 'User',
    'email': 'test_duplicate@example.com',
    'password1': 'TestPass123!',
    'password2': 'TestPass123!',
}

form = StudentRegistrationForm(form_data)
if form.is_valid():
    print("❌ FAIL: Form should have rejected duplicate student_id")
else:
    print("✓ PASS: Form correctly rejected duplicate student_id")
    if 'student_id' in form.errors:
        print(f"  Error message: {form.errors['student_id']}")

# Test 2: Valid unique data
print("\n" + "=" * 60)
print("Test 2: Valid unique student_id (should pass)")
print("=" * 60)
form_data_valid = {
    'username': 'new_student_test',
    'student_id': 'STU999',  # Unique
    'first_name': 'New',
    'last_name': 'Student',
    'email': 'newstudent_test@example.com',
    'password1': 'TestPass123!',
    'password2': 'TestPass123!',
}

form_valid = StudentRegistrationForm(form_data_valid)
if form_valid.is_valid():
    print("✓ PASS: Form accepted valid unique student_id")
else:
    print(f"❌ FAIL: Form rejected valid data:")
    for field, errors in form_valid.errors.items():
        print(f"  {field}: {errors}")

print("\n" + "=" * 60)
print("Validation tests complete!")
print("=" * 60)
