from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from eturesultapp.models import Student

class Command(BaseCommand):
    help = 'Backfill Student.user field by matching Student.email to User.email'

    def handle(self, *args, **options):
        User = get_user_model()
        matched = 0
        no_email = 0
        for student in Student.objects.all():
            if not student.email:
                no_email += 1
                continue
            try:
                user = User.objects.get(email__iexact=student.email)
            except User.DoesNotExist:
                continue
            except User.MultipleObjectsReturned:
                # skip ambiguous matches
                continue
            student.user = user
            student.save()
            matched += 1
        self.stdout.write(self.style.SUCCESS(f'Matched {matched} students. Skipped {no_email} students with no email.'))
