from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . import models


class StudentRegistrationForm(UserCreationForm):
    student_id = forms.CharField(max_length=20, required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    program = forms.CharField(max_length=128, required=False)
    department = forms.CharField(max_length=128, required=False)
    faculty = forms.CharField(max_length=128, required=False)

    class Meta:
        model = User
        fields = ('username', 'student_id', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_student_id(self):
        """Validate that student_id is unique."""
        student_id = self.cleaned_data.get('student_id')
        if student_id and models.Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError('A student with this ID already exists.')
        return student_id

    def clean_email(self):
        """Validate that email is unique."""
        email = self.cleaned_data.get('email')
        if email and models.Student.objects.filter(email=email).exists():
            raise forms.ValidationError('A student with this email already exists.')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered with another account.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data.get('email') or ''
        if commit:
            user.save()
            # create or update student profile (use get_or_create for safety)
            student, created = models.Student.objects.get_or_create(
                student_id=self.cleaned_data['student_id'],
                defaults={
                    'user': user,
                    'first_name': self.cleaned_data['first_name'],
                    'last_name': self.cleaned_data['last_name'],
                    'email': self.cleaned_data.get('email') or '',
                    'program': self.cleaned_data.get('program') or '',
                    'department': self.cleaned_data.get('department') or '',
                    'faculty': self.cleaned_data.get('faculty') or '',
                }
            )
            # If student already existed, update it with the user link
            if not created:
                student.user = user
                student.first_name = self.cleaned_data['first_name']
                student.last_name = self.cleaned_data['last_name']
                student.email = self.cleaned_data.get('email') or ''
                student.save()
        return user


class LecturerRegistrationForm(UserCreationForm):
    staff_id = forms.CharField(max_length=20, required=True)
    department = forms.CharField(max_length=100, required=False)
    is_admin_assistant = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_staff_id(self):
        """Validate that staff_id is unique."""
        staff_id = self.cleaned_data.get('staff_id')
        if staff_id and models.Lecturer.objects.filter(staff_id=staff_id).exists():
            raise forms.ValidationError('A lecturer with this staff ID already exists.')
        return staff_id

    def clean_email(self):
        """Validate that email is unique."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email') or ''
        if commit:
            user.save()
            lecturer, created = models.Lecturer.objects.get_or_create(
                staff_id=self.cleaned_data['staff_id'],
                defaults={
                    'user': user,
                    'department': self.cleaned_data.get('department') or '',
                    'is_admin_assistant': self.cleaned_data.get('is_admin_assistant', False),
                }
            )
            # If lecturer already existed, update the user link
            if not created:
                lecturer.user = user
                lecturer.save()
        return user


class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    registration_code = forms.CharField(max_length=128, required=False, help_text='Admin registration code (if required)')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        """Validate that email is unique."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email') or ''
        # mark as staff; superuser flag should be set manually if needed
        user.is_staff = True
        if commit:
            user.save()
        return user
