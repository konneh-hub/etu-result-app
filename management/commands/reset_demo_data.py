"""
Management command to safely reset or clear demo/test data.
Use with caution in production.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from eturesultapp.models import Student, Lecturer, Course, Result


class Command(BaseCommand):
    help = 'Reset or clear demo/test data safely'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Delete all users, students, lecturers, courses, and results',
        )
        parser.add_argument(
            '--clear-inactive',
            action='store_true',
            help='Delete all inactive users and their related profiles',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        if options.get('clear_all'):
            self.clear_all_data(dry_run)
        elif options.get('clear_inactive'):
            self.clear_inactive_users(dry_run)
        else:
            self.stdout.write(
                self.style.WARNING(
                    'No action specified. Use --clear-all or --clear-inactive'
                )
            )

    def clear_all_data(self, dry_run=False):
        """Delete all app data."""
        self.stdout.write(self.style.WARNING('Clearing all data...'))
        
        if dry_run:
            self.stdout.write(f'  Would delete {Result.objects.count()} results')
            self.stdout.write(f'  Would delete {Student.objects.count()} students')
            self.stdout.write(f'  Would delete {Lecturer.objects.count()} lecturers')
            self.stdout.write(f'  Would delete {Course.objects.count()} courses')
            self.stdout.write(f'  Would delete {User.objects.count()} users')
            self.stdout.write(self.style.SUCCESS('DRY RUN: No data deleted'))
        else:
            Result.objects.all().delete()
            self.stdout.write(f'  Deleted results')
            Student.objects.all().delete()
            self.stdout.write(f'  Deleted students')
            Lecturer.objects.all().delete()
            self.stdout.write(f'  Deleted lecturers')
            Course.objects.all().delete()
            self.stdout.write(f'  Deleted courses')
            User.objects.all().delete()
            self.stdout.write(f'  Deleted users')
            self.stdout.write(self.style.SUCCESS('All data cleared'))

    def clear_inactive_users(self, dry_run=False):
        """Delete inactive users and related profiles."""
        inactive_users = User.objects.filter(is_active=False)
        count = inactive_users.count()
        
        self.stdout.write(f'Found {count} inactive users')
        
        if dry_run:
            self.stdout.write('DRY RUN: Would delete:')
            for user in inactive_users:
                self.stdout.write(f'  - {user.username} ({user.email})')
            self.stdout.write(self.style.SUCCESS('DRY RUN: No data deleted'))
        else:
            for user in inactive_users:
                self.stdout.write(f'Deleting inactive user: {user.username}')
            inactive_users.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {count} inactive users'))
