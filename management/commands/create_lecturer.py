from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from eturesultapp.models import Lecturer
import getpass


class Command(BaseCommand):
    help = 'Create a new lecturer account with associated user permissions'

    def add_arguments(self, parser):
        parser.add_argument('staff_id', type=str, help='Staff ID for the lecturer')
        parser.add_argument('email', type=str, help='Email address for the lecturer')
        parser.add_argument('first_name', type=str, help='First name of the lecturer')
        parser.add_argument('last_name', type=str, help='Last name of the lecturer')
        parser.add_argument('department', type=str, help='Department of the lecturer')
        parser.add_argument(
            '--admin-assistant',
            action='store_true',
            help='Make the lecturer an admin assistant'
        )

    def handle(self, *args, **options):
        # Get password securely
        while True:
            password = getpass.getpass('Enter password for the lecturer: ')
            password_confirm = getpass.getpass('Confirm password: ')
            
            if password != password_confirm:
                self.stdout.write(self.style.ERROR('Passwords do not match. Please try again.'))
                continue
            
            try:
                validate_password(password)
                break
            except ValidationError as e:
                self.stdout.write(self.style.ERROR('\n'.join(e.messages)))

        try:
            # Create user account
            user = User.objects.create_user(
                username=options['email'],
                email=options['email'],
                password=password,
                first_name=options['first_name'],
                last_name=options['last_name']
            )

            # Create lecturer profile
            lecturer = Lecturer.objects.create(
                user=user,
                staff_id=options['staff_id'],
                department=options['department'],
                is_admin_assistant=options['admin_assistant']
            )

            # Set up permissions
            lecturer_group, created = Group.objects.get_or_create(name='Lecturers')
            if created:
                # Add default lecturer permissions
                permissions = [
                    'view_student', 'view_course', 'view_result',
                    'add_result', 'change_result', 'delete_result',
                ]
                for perm in permissions:
                    lecturer_group.permissions.add(
                        Permission.objects.get(codename=perm)
                    )

            # If admin assistant, add extra permissions
            if options['admin_assistant']:
                admin_assistant_group, created = Group.objects.get_or_create(name='Admin Assistants')
                if created:
                    # Add admin assistant permissions
                    permissions = [
                        'add_student', 'change_student', 'delete_student',
                        'add_course', 'change_course', 'delete_course',
                        'view_lecturer',
                    ]
                    for perm in permissions:
                        admin_assistant_group.permissions.add(
                            Permission.objects.get(codename=perm)
                        )
                user.groups.add(admin_assistant_group)

            # Add to lecturer group
            user.groups.add(lecturer_group)

            self.stdout.write(self.style.SUCCESS(
                f'Successfully created lecturer account for {user.get_full_name()} ({options["staff_id"]})'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating lecturer account: {str(e)}'))