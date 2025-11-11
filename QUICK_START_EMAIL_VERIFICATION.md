# Quick Start: Email Verification for Registrations

## What Changed?
Your registration system now requires email verification:
1. Users register → get validation checks for duplicate ID/email
2. Inactive account created + activation email sent
3. Users click email link to activate → auto-logged in → dashboard

## For Development/Testing

### Start the server:
```bash
cd C:\ETU_Ruslts
python manage.py runserver
```

### Register a new student:
1. Go to http://127.0.0.1:8000/register/student/
2. Fill in form (use unique student_id, e.g., `TEST001`)
3. Include a valid email
4. Submit

### Watch the console:
The activation email will print to the terminal where the dev server runs. You'll see:
```
Subject: Activate your ETU Results account
To: student@example.com

Hello Student_Name,

Thank you for registering at ETU Results.

Please click the link below to activate your account:

http://127.0.0.1:8000/activate/base64-uid/token-string/

...
```

### Activate:
Copy the activation URL from the console and paste it into your browser. You'll be auto-logged in and redirected to the student dashboard.

## Form Validation

The forms now check for duplicates before saving:
- ❌ Duplicate student_id → Shows "A student with this ID already exists"
- ❌ Duplicate email → Shows "A student with this email already exists"
- ✓ Valid unique data → Creates account and sends activation email

## If You Have Old Test Data

Clear inactive users:
```bash
python manage.py reset_demo_data --clear-inactive
```

Or clear everything:
```bash
python manage.py reset_demo_data --clear-all
```

## Template Changes

New templates (check your emails):
- `activation_email.txt` — Email body
- `registration_complete.html` — "Check your email" page
- `activation_invalid.html` — Invalid token page

## Files Changed

**Modified:**
- `eturesultapp/forms.py` — Added validation + email required
- `eturesultapp/views.py` — Added email sending + activation flow
- `eturesultapp/urls.py` — Added activation URLs

**Created:**
- `eturesultapp/management/commands/reset_demo_data.py` — Data cleanup
- `test_form_validation.py` — Test script

## Next Steps

✓ Form validation working
✓ Email sending setup (console backend for dev)
✓ Activation flow working
✓ Role-based dashboard redirects working

### Optional Enhancements:
- Add "Resend activation email" button
- Switch to HTML email templates
- Add tests for registration flow
- Configure real SMTP for production

## Need Help?

All forms now validate before saving, preventing the UNIQUE constraint error. If you get duplicate errors:
1. Check if student_id/email already exists
2. Use `reset_demo_data` to clear old test accounts
3. Register with a new unique student_id

Enjoy your new email verification system! 🎉
