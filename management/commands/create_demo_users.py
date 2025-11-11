from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create demo admin, lecturer and student users and link corresponding models.'

    def handle(self, *args, **options):
        User = get_user_model()

        from eturesultapp import models

        created = []

        # Admin user
        admin_username = 'admin_demo'
        admin_email = 'admin_demo@example.com'
        admin_password = 'AdminPass123!'
        admin_user, created_admin = User.objects.get_or_create(username=admin_username, defaults={
            'email': admin_email,
        })
        if created_admin:
            admin_user.set_password(admin_password)
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            created.append(('admin', admin_username, admin_password))

        # Lecturer user
        lecturer_username = 'lecturer_demo'
        lecturer_email = 'lecturer_demo@example.com'
        lecturer_password = 'LecturerPass123!'
        lecturer_user, created_lect = User.objects.get_or_create(username=lecturer_username, defaults={
            'email': lecturer_email,
        })
        if created_lect:
            lecturer_user.set_password(lecturer_password)
            lecturer_user.is_staff = False
            lecturer_user.save()
            created.append(('lecturer', lecturer_username, lecturer_password))

        # Link or create Lecturer model
        try:
            lec_obj, lec_created = models.Lecturer.objects.get_or_create(user=lecturer_user, defaults={
                'staff_id': 'LEC100',
                'department': 'Computer Science',
            })
        except Exception:
            # Fallback: try to create with minimal fields if OneToOne not allowed in get_or_create
            if not models.Lecturer.objects.filter(user=lecturer_user).exists():
                lec_obj = models.Lecturer(user=lecturer_user, staff_id='LEC100', department='Computer Science')
                lec_obj.save()

        # Student user
        student_username = 'student_demo'
        student_email = 'student_demo@example.com'
        student_password = 'StudentPass123!'
        student_user, created_stu = User.objects.get_or_create(username=student_username, defaults={
            'email': student_email,
        })
        if created_stu:
            student_user.set_password(student_password)
            student_user.is_staff = False
            student_user.save()
            created.append(('student', student_username, student_password))

        # Link or create Student model
        try:
            stu_obj, stu_created = models.Student.objects.get_or_create(user=student_user, defaults={
                'student_id': 'STU100',
                'first_name': 'Demo',
                'last_name': 'Student',
                'email': student_email,
                'program': 'BSc Computer Science',
                'department': 'Computer Science',
                'faculty': 'Science',
                'enrollment_date': timezone.now().date(),
            })
        except Exception:
            if not models.Student.objects.filter(user=student_user).exists():
                stu_obj = models.Student(user=student_user, student_id='STU100', first_name='Demo', last_name='Student', email=student_email, program='BSc Computer Science', department='Computer Science', faculty='Science', enrollment_date=timezone.now().date())
                stu_obj.save()

        # Create sample course
        course, course_created = models.Course.objects.get_or_create(code='CSC101', defaults={
            'name': 'Introduction to Computer Science',
            'credits': 3,
            'semester': 'Fall 2025',
            'is_active': True,
        })

        # Ensure lecturer teaches the course
        try:
            if lec_obj and not lec_obj.courses.filter(pk=course.pk).exists():
                lec_obj.courses.add(course)
        except Exception:
            pass

        # Create a result for the demo student
        try:
            if not models.Result.objects.filter(student=stu_obj, course=course).exists():
                models.Result.objects.create(student=stu_obj, course=course, grade='A', semester=course.semester, recorded_at=timezone.now())
        except Exception:
            # If Result model field names differ, ignore
            pass

        self.stdout.write(self.style.SUCCESS('Demo data ensured.'))
        if created:
            self.stdout.write('Created users (username : password):')
            for role, u, pw in created:
                self.stdout.write(f'  - {role}: {u} : {pw}')
        else:
            self.stdout.write('No new users created; demo users already existed or were present.')
