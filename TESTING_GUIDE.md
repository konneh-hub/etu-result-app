# Quick Start Testing Guide

## Prerequisites
- Python 3.8+
- Django 5.2.7+
- SQLite3
- Admin user created
- At least one Lecturer record
- At least one Student record

## Starting the Server

```powershell
# Navigate to project directory
cd c:\ETU_Ruslts

# Run migrations (if needed)
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start development server
python manage.py runserver
```

Server will be available at: `http://127.0.0.1:8000/`

## Testing the Three Dashboards

### 1. Admin Dashboard Test

**Step 1: Access Login Page**
- URL: `http://127.0.0.1:8000/accounts/login/`
- You should see a modern purple gradient login form

**Step 2: Login as Admin**
- Use superuser credentials
- Click "Sign In"

**Step 3: Verify Admin Dashboard**
- You should be redirected to `/dashboard/`
- Should see 4 statistics cards:
  - Total Students (Blue)
  - Active Courses (Green)
  - Lecturers (Cyan)
  - Results Recorded (Yellow)
- Should see "Recent Results Posted" table
- Should see "Quick Actions" menu with 6 items
- Should see system tips

**Step 4: Test Navigation**
- Click "Dashboard" in sidebar → Should stay on page
- Click "Students" in sidebar → Should go to student list
- Click "Courses" → Should show courses
- Click "Lecturers" → Should show lecturers
- Click "Results" → Should show results

**Step 5: Test User Menu**
- Click user dropdown (top right) → Should show options:
  - Admin Panel
  - Dashboard
  - Logout

### 2. Lecturer Dashboard Test

**Step 1: Logout**
- Click user dropdown (top right)
- Click "Logout"

**Step 2: Login as Lecturer**
- URL: `http://127.0.0.1:8000/accounts/login/`
- Use lecturer's username (from Lecturer record)
- Click "Sign In"

**Step 3: Verify Lecturer Dashboard**
- You should see:
  - Header with "Lecturer Dashboard"
  - Lecturer name and Staff ID
  - 3 statistics cards:
    - Active Courses
    - Total Students
    - Results Recorded
  - Lecturer Information section with:
    - Full Name
    - Staff ID
    - Department
    - Email
    - Role badges
  - "My Assigned Courses" table
  - Quick Actions menu

**Step 4: Test Courses Section**
- Should display courses assigned to this lecturer
- Each course should show:
  - Code
  - Name
  - Semester (as badge)
  - Credits
  - "Manage Results" button

**Step 5: Test Quick Actions**
- "Manage Results" → Should open results page
- "View All Students" → Should show student list
- "Record New Result" → Should open result creation form
- If admin assistant: "Admin Panel" → Should open Django admin

### 3. Student Dashboard Test

**Step 1: Logout**
- Click user dropdown
- Click "Logout"

**Step 2: Login as Student**
- URL: `http://127.0.0.1:8000/accounts/login/`
- Use student username
- Click "Sign In"

**Step 3: Verify Student Dashboard**
- You should see:
  - Header with "My Academic Dashboard"
  - Student ID displayed
  - Profile card with:
    - Student avatar
    - Full name
    - Program
    - Department
    - Faculty
    - Enrollment date
  - 3 statistics cards:
    - Current GPA
    - Total Courses
    - Results Posted
  - Personal Information section:
    - Email
    - Student ID
    - Program
    - Status (Active/Inactive badge)
  - (If available) Semester Summary table:
    - Semester name
    - Courses taken
    - Total points
    - Semester GPA
  - Results table with all grades:
    - Course Code
    - Course Name
    - Grade (as badge)
    - Credits
    - Semester
    - Points

**Step 4: Test Buttons**
- "Edit Profile" → Should open edit form
- "Download Results" → Should download CSV file

**Step 5: Verify Academic Information**
- GPA should be calculated correctly
- Results should be sorted (newest first)
- Grades should display with proper formatting
- All course information should be visible

## Mobile Responsive Testing

### Test on Tablet
- Open developer tools (F12)
- Set to tablet size (768px width)
- Verify:
  - Sidebar disappears
  - Hamburger menu appears
  - Grid layouts become 2 columns
  - Tables are still readable
  - All buttons accessible

### Test on Mobile
- Set to mobile size (375px width)
- Verify:
  - Single column layout
  - Navigation works via hamburger menu
  - Text is readable (no horizontal scroll)
  - Buttons are touch-friendly
  - Tables scroll horizontally if needed

## Common Issues & Solutions

### Issue: "Page not found" after login
**Solution**:
- Run `python manage.py migrate`
- Ensure `/dashboard/` URL pattern exists
- Check DashboardView is registered in urls.py

### Issue: Wrong dashboard displayed
**Solution**:
- Verify user.is_superuser value for admin
- Check Lecturer record exists for lecturer
- Check Student record email matches user email

### Issue: Static files not loading
**Solution**:
- Run `python manage.py collectstatic --noinput`
- If DEBUG=True, static should be served automatically
- Check STATIC_URL and STATIC_ROOT in settings.py

### Issue: Sidebar not showing
**Solution**:
- Ensure user is authenticated (logged in)
- Check responsive breakpoint (sidebar hidden < 1024px)
- Verify CSS file loaded (check browser console for 404)

### Issue: Icons not displaying
**Solution**:
- Check Font Awesome CDN is accessible
- Verify icons use correct class names (fas fa-*)
- Check browser console for loading errors

## Performance Notes

- Dashboard loads statistics on each request
- Consider caching for large datasets
- Tables paginate at 10 items (configurable)
- All queries use select_related() for optimization
- CSS is minified for production

## Keyboard Shortcuts (Optional)

Add these to improve accessibility:
- Alt + D = Go to Dashboard
- Alt + L = Logout
- Alt + M = Toggle Menu

## Next Steps

After testing:
1. ✅ Run full test suite
2. ✅ Check browser console for errors
3. ✅ Verify all links work
4. ✅ Test with different browsers
5. ✅ Load test with multiple users
6. ✅ Deploy to production

## Getting Help

If you encounter issues:

1. Check `python manage.py shell` for data:
```python
from django.contrib.auth.models import User
from eturesultapp.models import Lecturer, Student

# Check users
print(User.objects.all())

# Check lecturers
print(Lecturer.objects.all())

# Check students
print(Student.objects.all())
```

2. View server logs for errors:
- Check console output while server is running
- Look for ValueError, AttributeError, etc.

3. Browser developer console (F12):
- Check for JavaScript errors
- Verify CSS loaded (Network tab)
- Check HTML structure (Elements tab)

---

**Test Completed**: [Date/Time]
**Tester**: [Your Name]
**Status**: ✅ Ready for Production

