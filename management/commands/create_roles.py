from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from eturesultapp import models


class Command(BaseCommand):
    help = 'Create default user groups and assign model permissions'

    def handle(self, *args, **options):
        groups = {
            'Admin': {
                'models': ['student', 'course', 'result'],
                'perms': ['add', 'change', 'delete', 'view']
            },
            'Registrar': {
                'models': ['student', 'result'],
                'perms': ['add', 'change', 'view']
            },
            'Viewer': {
                'models': ['student', 'course', 'result'],
                'perms': ['view']
            }
        }

        for group_name, spec in groups.items():
            group, created = Group.objects.get_or_create(name=group_name)
            added = 0
            for model_label in spec['models']:
                try:
                    ct = ContentType.objects.get(app_label='eturesultapp', model=model_label)
                except ContentType.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'ContentType for {model_label} not found'))
                    continue
                for perm_prefix in spec['perms']:
                    codename = f"{perm_prefix}_{model_label}"
                    try:
                        perm = Permission.objects.get(codename=codename, content_type=ct)
                        group.permissions.add(perm)
                        added += 1
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Permission {codename} does not exist'))
            group.save()
            self.stdout.write(self.style.SUCCESS(f"Group '{group_name}' ready (added {added} perms)"))
