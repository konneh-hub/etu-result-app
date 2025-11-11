from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Student, Course, Result


class ModelsTestCase(TestCase):
    def test_create_student_course_result(self):
        s = Student.objects.create(student_id='S001', first_name='John', last_name='Doe')
        c = Course.objects.create(code='CS101', name='Intro CS', credits=3)
        r = Result.objects.create(student=s, course=c, grade='A', semester='2025-1')

        self.assertEqual(Student.objects.count(), 1)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Result.objects.count(), 1)
        self.assertEqual(str(s).split(' - ')[0], 'S001')


class ViewsTestCase(TestCase):
    def setUp(self):
        self.student = Student.objects.create(student_id='S002', first_name='Jane', last_name='Smith')
        self.course = Course.objects.create(code='MATH1', name='Mathematics', credits=4)

    def test_student_list_view(self):
        resp = self.client.get(reverse('eturesultapp:student_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Students')

    def test_student_detail_view(self):
        resp = self.client.get(reverse('eturesultapp:student_detail', args=[self.student.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.student.student_id)

    def test_student_create_via_post(self):
        # create a user with permission to add students and login
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_superuser(username='creator', email='c@x.com', password='pw')
        self.client.login(username='creator', password='pw')

        data = {'student_id': 'S003', 'first_name': 'Alan', 'last_name': 'Turing', 'email': 'alan@example.com'}
        resp = self.client.post(reverse('eturesultapp:student_create'), data)
        # successful create redirects to success_url which is 'student_list'
        self.assertIn(resp.status_code, (302, 303))
        self.assertTrue(Student.objects.filter(student_id='S003').exists())
        
    def test_student_list_search(self):
        resp = self.client.get(reverse('eturesultapp:student_list') + '?search=Jane')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Jane')
        self.assertNotContains(resp, 'Alan')

    def test_course_list_view(self):
        resp = self.client.get(reverse('eturesultapp:course_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'MATH1')


class APITests(APITestCase):
    def setUp(self):
        self.student = Student.objects.create(
            student_id='S004', 
            first_name='Grace', 
            last_name='Hopper'
        )
        self.course = Course.objects.create(
            code='CS102',
            name='Programming',
            credits=3
        )
        
    def test_list_students(self):
        url = '/api/students/'  # URL pattern from router registration
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_create_result(self):
        url = '/api/results/'  # URL pattern from router registration
        data = {
            'student': self.student.id,
            'course': self.course.id,
            'grade': 'A',
            'semester': '2025-1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Result.objects.count(), 1)
        self.course = Course.objects.create(
            code='CS102',
            name='Programming',
            credits=3
        )
        
    def test_list_students(self):
        url = '/api/students/'  # URL pattern from router registration
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('results' in data, 'Response should be paginated')
        self.assertEqual(len(data['results']), 1)  # Only one student created in setUp
        
    def test_create_result(self):
        url = '/api/students/'  # Use hardcoded URL since router URLs don't use reverse
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_create_result(self):
        url = '/api/results/'  # Use hardcoded URL since router URLs don't use reverse
        data = {
            'student_id': self.student.id,
            'course_id': self.course.id,
            'grade': 'A',
            'semester': '2025-1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Result.objects.count(), 1)


class DashboardAuthTests(TestCase):
    def test_dashboard_requires_login(self):
        resp = self.client.get(reverse('eturesultapp:dashboard'))
        # should redirect to login
        self.assertIn(resp.status_code, (302, 303))

    def test_dashboard_shows_stats_when_logged_in(self):
        # create a user and log in
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username='tester', password='pass')
        self.client.login(username='tester', password='pass')
        resp = self.client.get(reverse('eturesultapp:dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Welcome')


class RolesCommandTests(TestCase):
    def test_create_roles_command_creates_groups(self):
        from django.core.management import call_command
        from django.contrib.auth.models import Group
        # run command
        call_command('create_roles')
        self.assertTrue(Group.objects.filter(name='Admin').exists())
        self.assertTrue(Group.objects.filter(name='Registrar').exists())
        self.assertTrue(Group.objects.filter(name='Viewer').exists())


class AdminExportAndRoleUITests(TestCase):
    def test_student_admin_export_returns_csv(self):
        # create sample students
        s1 = Student.objects.create(student_id='S100', first_name='Alice', last_name='A')
        s2 = Student.objects.create(student_id='S101', first_name='Bob', last_name='B')

        # create a superuser to simulate admin
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_user = User.objects.create_superuser(username='adm', email='adm@x.com', password='pass')

        # call admin action directly
        from django.test import RequestFactory
        from django.contrib import admin as django_admin
        from eturesultapp.admin import StudentAdmin

        rf = RequestFactory()
        request = rf.get('/admin/eturesultapp/student/')
        request.user = admin_user

        sa = StudentAdmin(Student, django_admin.site)
        response = sa.export_as_csv(request, Student.objects.all())
        self.assertEqual(response.status_code, 200)
        self.assertIn('students_export.csv', response['Content-Disposition'])
        text = response.content.decode('utf-8-sig')  # handle BOM
        self.assertIn('student_id', text)

    def test_viewer_group_cannot_see_add_links(self):
        # ensure groups exist
        from django.core.management import call_command
        call_command('create_roles')

        # create a viewer user and add to Viewer group
        from django.contrib.auth.models import Group
        viewer_group = Group.objects.get(name='Viewer')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        viewer = User.objects.create_user(username='viewer1', password='pw')
        viewer.groups.add(viewer_group)

        # login and request dashboard
        self.client.login(username='viewer1', password='pw')
        resp = self.client.get(reverse('eturesultapp:dashboard'))
        self.assertEqual(resp.status_code, 200)
        # Quick action 'Add Student' should NOT be visible for viewer
        self.assertNotContains(resp, 'Add Student')


class LoginRedirectTests(TestCase):
    def test_admin_redirects_to_admin_dashboard(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_superuser(username='adm2', email='adm2@x.com', password='pw')
        # use client POST to hit the login view
        resp = self.client.post('/accounts/login/', {'username': 'adm2', 'password': 'pw'})
        self.assertIn(resp.status_code, (302, 303))
        self.assertIn('/dashboard/admin/', resp['Location'])

    def test_lecturer_redirects_to_lecturer_dashboard(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username='lect1', email='lect1@x.com', password='pw')
        # create lecturer profile
        from .models import Lecturer
        Lecturer.objects.create(user=user, staff_id='L001', department='Dept')
        resp = self.client.post('/accounts/login/', {'username': 'lect1', 'password': 'pw'})
        self.assertIn(resp.status_code, (302, 303))
        self.assertIn('/dashboard/lecturer/', resp['Location'])

    def test_student_redirects_to_student_dashboard(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username='stud1', email='stud1@x.com', password='pw')
        from .models import Student
        Student.objects.create(student_id='S900', first_name='Stu', last_name='Dent', email='stud1@x.com')
        resp = self.client.post('/accounts/login/', {'username': 'stud1', 'password': 'pw'})
        self.assertIn(resp.status_code, (302, 303))
        self.assertIn('/dashboard/student/', resp['Location'])


class StudentDownloadTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='suser', email='suser@x.com', password='pw')
        self.student = Student.objects.create(student_id='S500', first_name='Don', last_name='Quixote', email='suser@x.com')

    def test_student_can_download_own_results(self):
        # login and download
        self.client.login(username='suser', password='pw')
        resp = self.client.get(reverse('eturesultapp:student_download', args=[self.student.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/csv', resp['Content-Type'])
        text = resp.content.decode('utf-8-sig')
        self.assertIn('S500', text)

    def test_other_user_cannot_download(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other = User.objects.create_user(username='other', email='other@x.com', password='pw')
        self.client.login(username='other', password='pw')
        resp = self.client.get(reverse('eturesultapp:student_download', args=[self.student.pk]))
        self.assertEqual(resp.status_code, 403)

    def test_student_can_edit_own_profile(self):
        # login as student and post edits
        self.client.login(username='suser', password='pw')
        url = reverse('eturesultapp:student_edit_self', args=[self.student.pk])
        resp = self.client.post(url, {'program': 'Computer Science', 'department': 'CS', 'faculty': 'Engineering', 'email': 'suser@x.com'})
        self.assertIn(resp.status_code, (302, 303))
        self.student.refresh_from_db()
        self.assertEqual(self.student.program, 'Computer Science')

    def test_other_user_cannot_edit_student(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other = User.objects.create_user(username='other2', email='other2@x.com', password='pw')
        self.client.login(username='other2', password='pw')
        url = reverse('eturesultapp:student_edit_self', args=[self.student.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_staff_can_edit_any_student(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        staff = User.objects.create_user(username='staff2', email='staff2@x.com', password='pw', is_staff=True)
        self.client.login(username='staff2', password='pw')
        url = reverse('eturesultapp:student_edit_self', args=[self.student.pk])
        resp = self.client.post(url, {'program': 'Maths', 'department': 'Math', 'faculty': 'Science', 'email': self.student.email})
        self.assertIn(resp.status_code, (302, 303))
        self.student.refresh_from_db()
        self.assertEqual(self.student.program, 'Maths')


class ExportResultsEndpointTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.staff = User.objects.create_user(username='staff', email='staff@x.com', password='pw', is_staff=True)
        self.viewer = User.objects.create_user(username='viewer2', email='viewer2@x.com', password='pw')
        # create a sample result
        s = Student.objects.create(student_id='SX1', first_name='Ex', last_name='Ample')
        c = Course.objects.create(code='T101', name='Test', credits=3)
        Result.objects.create(student=s, course=c, grade='A', semester='2025-1')

    def test_staff_can_export_all_results(self):
        self.client.login(username='staff', password='pw')
        resp = self.client.get(reverse('eturesultapp:export_results'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/csv', resp['Content-Type'])

    def test_non_staff_cannot_export_all_results(self):
        self.client.login(username='viewer2', password='pw')
        resp = self.client.get(reverse('eturesultapp:export_results'))
        self.assertEqual(resp.status_code, 403)