import os
import django

# Make sure we run from project root
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ETU_Ruslts.settings')
# Adjust Python path if necessary
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'admin'
password = '1234'
email = 'admin@example.com'

user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'is_staff': True, 'is_superuser': True})
if created:
    user.set_password(password)
    user.save()
    print(f"Created superuser '{username}' with provided password.")
else:
    # Ensure it has staff/superuser and update password
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    print(f"Updated existing user '{username}' to superuser and set provided password.")
