from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from django.urls import reverse_lazy
from datetime import datetime
from . import models, forms
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
import csv

class SidebarContextMixin:
    """Mixin to add sidebar context to views."""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_sidebar'] = True
        return context
 


def home_view(request):
    """Landing page for users to choose registration type or log in."""
    if request.user.is_authenticated:
        return redirect('eturesultapp:dashboard')
    return render(request, 'eturesultapp/home.html')

class DashboardView(LoginRequiredMixin, generic.View):
    def get(self, request):
        if request.user.is_superuser:
            return self.admin_dashboard(request)
        
        try:
            lecturer = models.Lecturer.objects.get(user=request.user)
            return self.lecturer_dashboard(request, lecturer)
        except models.Lecturer.DoesNotExist:
            try:
                student = models.Student.objects.get(email=request.user.email)
                return self.student_dashboard(request, student)
            except models.Student.DoesNotExist:
                # Redirect to a default view if user type cannot be determined
                return self.admin_dashboard(request)  # Show admin view as default

    def admin_dashboard(self, request):
        context = {
            'total_students': models.Student.objects.count(),
            'total_courses': models.Course.objects.filter(is_active=True).count(),
            'total_lecturers': models.Lecturer.objects.count(),
            'total_results': models.Result.objects.count(),
            'recent_results': models.Result.objects.select_related('student', 'course').order_by('-recorded_at')[:5]
        }
        return render(request, 'eturesultapp/admin_dashboard.html', context)

    def lecturer_dashboard(self, request, lecturer):
        context = {
            'lecturer': lecturer,
            'total_students': models.Student.objects.count(),
            'total_courses': models.Course.objects.filter(is_active=True).count(),
            'total_results': models.Result.objects.filter(course__in=lecturer.courses.all()).count()
        }
        return render(request, 'eturesultapp/lecturer_dashboard.html', context)

    def student_dashboard(self, request, student):
        # Prefetch related course data to optimize queries
        results = student.results.select_related('course').order_by('-recorded_at')
        
        # Calculate semester summary
        semester_summary = {}
        for result in results:
            if result.semester not in semester_summary:
                semester_summary[result.semester] = {
                    'total_courses': 0,
                    'total_points': 0,
                    'gpa': 0.0
                }
            semester_summary[result.semester]['total_courses'] += 1
            semester_summary[result.semester]['total_points'] += result.get_grade_points()
        
        # Calculate GPA for each semester
        for semester in semester_summary:
            total_courses = semester_summary[semester]['total_courses']
            if total_courses > 0:
                semester_summary[semester]['gpa'] = (
                    semester_summary[semester]['total_points'] / total_courses
                )

        context = {
            'student': student,
            'results': results,
            'semester_summary': semester_summary,
            'total_courses': results.count(),
            'recent_results': results[:5]  # Last 5 results
        }
        return render(request, 'eturesultapp/student_dashboard.html', context)


class CustomLoginView(LoginView):
    """Redirect users to role-specific dashboard after login."""
    template_name = 'registration/login.html'

    def get_success_url(self):
        # Redirect users to their specific dashboard based on role.
        user = self.request.user

        # Superuser -> admin dashboard
        if user.is_superuser:
            return reverse_lazy('eturesultapp:dashboard_admin')

        # Lecturer -> lecturer dashboard (match by OneToOne user relation)
        try:
            if models.Lecturer.objects.filter(user=user).exists():
                return reverse_lazy('eturesultapp:dashboard_lecturer')
        except Exception:
            # If models not accessible for some reason, fall through
            pass

        # Student -> student dashboard (prefer user relation, fallback to email match)
        try:
            if models.Student.objects.filter(user=user).exists():
                return reverse_lazy('eturesultapp:dashboard_student')
            if user.email and models.Student.objects.filter(email=user.email).exists():
                return reverse_lazy('eturesultapp:dashboard_student')
        except Exception:
            pass

        # Default fallback (unified dashboard)
        return reverse_lazy('eturesultapp:dashboard')


def register_student_view(request):
    if request.method == 'POST':
        form = forms.StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in
            login(request, user)
            return redirect('eturesultapp:dashboard')
    else:
        form = forms.StudentRegistrationForm()
    return render(request, 'eturesultapp/register_student.html', {'form': form})

def register_lecturer_view(request):
    if request.method == 'POST':
        form = forms.LecturerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in
            login(request, user)
            return redirect('eturesultapp:dashboard')
    else:
        form = forms.LecturerRegistrationForm()
    return render(request, 'eturesultapp/register_lecturer.html', {'form': form})

def register_admin_view(request):
    if request.method == 'POST':
        form = forms.AdminRegistrationForm(request.POST)
        if form.is_valid():
            from django.conf import settings
            registration_code = form.cleaned_data.get('registration_code')
            if hasattr(settings, 'ADMIN_REGISTRATION_CODE') and settings.ADMIN_REGISTRATION_CODE:
                if registration_code != settings.ADMIN_REGISTRATION_CODE:
                    form.add_error('registration_code', 'Invalid registration code')
                    return render(request, 'eturesultapp/register_admin.html', {'form': form})
            
            user = form.save()
            # Log the user in
            login(request, user)
            return redirect('eturesultapp:dashboard')
    else:
        form = forms.AdminRegistrationForm()
    return render(request, 'eturesultapp/register_admin.html', {'form': form})

@login_required
def student_results_download(request, pk):
    """Allow a student to download their results as CSV. Staff can download any student's results."""
    # Ensure permission: student can download their own only, staff can download any
    student = get_object_or_404(models.Student, pk=pk)

    # If user is not staff/superuser, ensure their email matches the student record
    if not (request.user.is_staff or request.user.is_superuser):
        if request.user.email != (student.email or ''):
            return HttpResponse('Forbidden', status=403)

    # Build CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    # Add BOM for Excel compatibility
    response.write('\ufeff')
    filename = f"results_{student.student_id}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    # Header
    writer.writerow(['Student ID', 'Full Name', 'Program', 'Department', 'Faculty'])
    writer.writerow([student.student_id, f"{student.first_name} {student.last_name}", student.program or '', student.department or '', student.faculty or ''])
    writer.writerow([])
    # Results header
    writer.writerow(['Course Code', 'Course Name', 'Grade', 'Grade Points', 'Semester', 'Recorded At', 'Remarks'])

    for r in student.results.select_related('course').all():
        writer.writerow([r.course.code, r.course.name, r.grade, r.get_grade_points(), r.semester, r.recorded_at.isoformat(), r.remarks])

    return response


@login_required
def export_all_results(request):
    # Only allow staff or users with view_result permission
    if not (request.user.is_staff or request.user.has_perm('eturesultapp.view_result')):
        return HttpResponse('Forbidden', status=403)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response.write('\ufeff')
    response['Content-Disposition'] = 'attachment; filename="results_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Student Name', 'Course Code', 'Course Name', 'Grade', 'Grade Points', 'Semester', 'Recorded At'])
    qs = models.Result.objects.select_related('student', 'course').all().order_by('student__student_id')
    for r in qs:
        writer.writerow([r.student.student_id, f"{r.student.first_name} {r.student.last_name}", r.course.code, r.course.name, r.grade, r.get_grade_points(), r.semester, r.recorded_at.isoformat()])
    return response


def admin_dashboard_view(request):
    """Public wrapper to render admin dashboard (used for direct redirects)."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('eturesultapp:dashboard')
    context = {
        'total_students': models.Student.objects.count(),
        'total_courses': models.Course.objects.filter(is_active=True).count(),
        'total_lecturers': models.Lecturer.objects.count(),
        'total_results': models.Result.objects.count(),
        'recent_results': models.Result.objects.select_related('student', 'course').order_by('-recorded_at')[:5]
    }
    return render(request, 'eturesultapp/admin_dashboard.html', context)


def home_view(request):
    """Public home page: if user is authenticated, show the dashboard; otherwise show a marketing home page."""
    if request.user.is_authenticated:
        # Delegate to the existing DashboardView (TemplateView) to render dashboard
        return DashboardView.as_view()(request)
    return render(request, 'eturesultapp/home.html')


def register_student_view(request):
    from .forms import StudentRegistrationForm
    from django.contrib import messages

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create inactive user and linked student record, then send activation email
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                # create or update student profile (form.save will handle this)
                # We call save again to trigger the profile creation logic
                form.save(commit=True)

                # send activation email
                send_activation_email(request, user, user.email)

                messages.success(request, 'Registration successful! Please check your email to activate your account.')
                return redirect('eturesultapp:registration_complete')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    else:
        form = StudentRegistrationForm()
    return render(request, 'eturesultapp/register_student.html', {'form': form})


def register_lecturer_view(request):
    from .forms import LecturerRegistrationForm
    from django.contrib import messages

    if request.method == 'POST':
        form = LecturerRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                form.save(commit=True)

                send_activation_email(request, user, user.email)
                messages.success(request, 'Registration successful! Please check your email to activate your account.')
                return redirect('eturesultapp:registration_complete')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    else:
        form = LecturerRegistrationForm()
    return render(request, 'eturesultapp/register_lecturer.html', {'form': form})


def register_admin_view(request):
    from .forms import AdminRegistrationForm
    from django.contrib import messages

    require_code = getattr(settings, 'ADMIN_REGISTRATION_CODE', None)

    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('registration_code')
            if require_code and code != require_code:
                form.add_error('registration_code', 'Invalid admin registration code')
            else:
                try:
                    user = form.save(commit=False)
                    # mark as staff; admin activation required
                    user.is_staff = True
                    user.is_active = False
                    user.save()

                    # Optionally make superuser if setting allows
                    if getattr(settings, 'MAKE_ADMIN_SUPERUSER_ON_REGISTRATION', False):
                        user.is_superuser = True
                        user.save()

                    send_activation_email(request, user, user.email)
                    messages.success(request, 'Admin registration successful! Please check your email to activate your account.')
                    return redirect('eturesultapp:registration_complete')
                except Exception as e:
                    messages.error(request, f'Registration failed: {str(e)}')
    else:
        form = AdminRegistrationForm()
    return render(request, 'eturesultapp/register_admin.html', {'form': form, 'require_code': require_code})


def registration_complete(request):
    """Simple page shown after sign-up instructing user to check email for activation."""
    return render(request, 'eturesultapp/registration_complete.html')


def activate_account(request, uidb64, token):
    """Activate user account from email link."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = models.User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        # Ensure linked profiles exist (in case they were not created earlier)
        if not models.Lecturer.objects.filter(user=user).exists() and hasattr(user, 'lecturer'):
            pass
        # Log the user in and redirect to role-specific dashboard
        login(request, user)
        # Redirect based on role
        if user.is_superuser:
            return redirect('eturesultapp:dashboard_admin')
        if models.Lecturer.objects.filter(user=user).exists():
            return redirect('eturesultapp:dashboard_lecturer')
        if models.Student.objects.filter(user=user).exists() or (user.email and models.Student.objects.filter(email=user.email).exists()):
            return redirect('eturesultapp:dashboard_student')
        return redirect('eturesultapp:dashboard')
    else:
        return render(request, 'eturesultapp/activation_invalid.html')


def send_activation_email(request, user, to_email):
    """Helper to send activation email with tokenized link."""
    if not to_email:
        return

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_path = reverse('eturesultapp:activate', kwargs={'uidb64': uid, 'token': token})
    activation_link = request.build_absolute_uri(activation_path)

    subject = 'Activate your ETU Results account'
    message = render_to_string('eturesultapp/activation_email.txt', {
        'user': user,
        'activation_link': activation_link,
        'site_name': getattr(settings, 'SITE_NAME', 'ETU Results')
    })
    # Use console backend in development (settings already configured)
    send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'), [to_email], fail_silently=False)


def lecturer_dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('eturesultapp:dashboard')
    try:
        lecturer = models.Lecturer.objects.get(user=request.user)
    except models.Lecturer.DoesNotExist:
        return redirect('eturesultapp:dashboard')
    context = {
        'lecturer': lecturer,
        'total_students': models.Student.objects.count(),
        'total_courses': models.Course.objects.filter(is_active=True).count(),
        'total_results': models.Result.objects.filter(course__in=lecturer.courses.all()).count()
    }
    return render(request, 'eturesultapp/lecturer_dashboard.html', context)


def student_dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('eturesultapp:dashboard')
    try:
        student = models.Student.objects.get(email=request.user.email)
    except models.Student.DoesNotExist:
        return redirect('eturesultapp:dashboard')
    context = {'student': student}
    return render(request, 'eturesultapp/student_dashboard.html', context)


class LecturerListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    model = models.Lecturer
    permission_required = 'eturesultapp.view_lecturer'
    template_name = 'eturesultapp/lecturer_list.html'
    context_object_name = 'lecturers'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(staff_id__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        return queryset


class LecturerDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = models.Lecturer
    permission_required = 'eturesultapp.view_lecturer'
    template_name = 'eturesultapp/lecturer_detail.html'
    context_object_name = 'lecturer'


class LecturerCreateView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
    model = models.Lecturer
    permission_required = 'eturesultapp.add_lecturer'
    template_name = 'eturesultapp/lecturer_form.html'
    fields = ['staff_id', 'department', 'is_admin_assistant', 'courses']
    success_url = reverse_lazy('lecturer_list')


class LecturerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView):
    model = models.Lecturer
    permission_required = 'eturesultapp.change_lecturer'
    template_name = 'eturesultapp/lecturer_form.html'
    fields = ['staff_id', 'department', 'is_admin_assistant', 'courses']
    success_url = reverse_lazy('lecturer_list')


class LecturerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    model = models.Lecturer
    permission_required = 'eturesultapp.delete_lecturer'
    template_name = 'eturesultapp/lecturer_confirm_delete.html'
    success_url = reverse_lazy('lecturer_list')


class StudentListView(generic.ListView):
    model = models.Student
    template_name = 'eturesultapp/student_list.html'
    context_object_name = 'students'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student_id__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        return queryset.order_by('student_id')
class StudentDetailView(generic.DetailView):
    model = models.Student
    template_name = 'eturesultapp/student_detail.html'
    context_object_name = 'student'


class StudentSelfUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Allow a student to edit their own profile (program/department/faculty/email).

    Staff users with change permission can still use the regular StudentUpdateView.
    """
    model = models.Student
    template_name = 'eturesultapp/student_form.html'
    fields = ['program', 'department', 'faculty', 'email']

    def dispatch(self, request, *args, **kwargs):
        # Ensure the user is either staff (has change_student) or editing their own record
        self.object = self.get_object()
        if request.user.is_staff or request.user.has_perm('eturesultapp.change_student'):
            return super().dispatch(request, *args, **kwargs)

        # For regular users, ensure the logged-in user's email matches the student record
        if request.user.email and self.object.email and request.user.email.lower() == self.object.email.lower():
            return super().dispatch(request, *args, **kwargs)

        return HttpResponse('Forbidden', status=403)

    def get_success_url(self):
        return reverse_lazy('eturesultapp:dashboard_student')


class StudentCreateView(LoginRequiredMixin, PermissionRequiredMixin, SidebarContextMixin, generic.CreateView):
    model = models.Student
    permission_required = 'eturesultapp.add_student'
    fields = ['student_id', 'first_name', 'last_name', 'email', 'enrollment_date']
    template_name = 'eturesultapp/student_form.html'
    success_url = '/'


class StudentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SidebarContextMixin, generic.UpdateView):
    model = models.Student
    permission_required = 'eturesultapp.change_student'
    fields = ['student_id', 'first_name', 'last_name', 'email', 'enrollment_date']
    template_name = 'eturesultapp/student_form.html'
    success_url = '/'


class StudentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, SidebarContextMixin, generic.DeleteView):
    model = models.Student
    permission_required = 'eturesultapp.delete_student'
    template_name = 'eturesultapp/student_confirm_delete.html'
    success_url = '/'


class CourseListView(LoginRequiredMixin, SidebarContextMixin, generic.ListView):
    model = models.Course
    template_name = 'eturesultapp/course_list.html'
    context_object_name = 'courses'


class CourseCreateView(LoginRequiredMixin, PermissionRequiredMixin, SidebarContextMixin, generic.CreateView):
    model = models.Course
    permission_required = 'eturesultapp.add_course'
    fields = ['code', 'name', 'credits']
    template_name = 'eturesultapp/course_form.html'
    success_url = '/courses/'


class CourseUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SidebarContextMixin, generic.UpdateView):
    model = models.Course
    permission_required = 'eturesultapp.change_course'
    fields = ['code', 'name', 'credits']
    template_name = 'eturesultapp/course_form.html'
    success_url = '/courses/'


class CourseDeleteView(LoginRequiredMixin, PermissionRequiredMixin, SidebarContextMixin, generic.DeleteView):
    model = models.Course
    permission_required = 'eturesultapp.delete_course'
    template_name = 'eturesultapp/course_confirm_delete.html'
    success_url = '/courses/'


class ResultListView(LoginRequiredMixin, SidebarContextMixin, generic.ListView):
    model = models.Result
    template_name = 'eturesultapp/result_list.html'
    context_object_name = 'results'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(student__student_id__icontains=search) |
                models.Q(student__first_name__icontains=search) |
                models.Q(student__last_name__icontains=search) |
                models.Q(course__code__icontains=search)
            )
        return queryset.select_related('student', 'course').order_by('-recorded_at')
class ResultCreateView(LoginRequiredMixin, PermissionRequiredMixin, SidebarContextMixin, generic.CreateView):
    model = models.Result
    permission_required = 'eturesultapp.add_result'
    fields = ['student', 'course', 'grade', 'semester']
    template_name = 'eturesultapp/result_form.html'
    success_url = '/results/'


class ResultUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SidebarContextMixin, generic.UpdateView):
    model = models.Result
    permission_required = 'eturesultapp.change_result'
    fields = ['student', 'course', 'grade', 'semester']
    template_name = 'eturesultapp/result_form.html'
    success_url = '/results/'


class ResultDeleteView(LoginRequiredMixin, PermissionRequiredMixin, SidebarContextMixin, generic.DeleteView):
    model = models.Result
    permission_required = 'eturesultapp.delete_result'
    template_name = 'eturesultapp/result_confirm_delete.html'
    success_url = '/results/'


def get_current_semester():
    current_date = timezone.now()
    year = current_date.year
    month = current_date.month
    
    if month >= 8:  # August onwards is Fall semester
        semester = f"{year}-2"
    else:  # January to July is Spring semester
        semester = f"{year}-1"
    return semester


class DashboardView(LoginRequiredMixin, SidebarContextMixin, generic.TemplateView):
    template_name = 'eturesultapp/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get basic stats
        context['total_students'] = models.Student.objects.filter(is_active=True).count()
        context['total_courses'] = models.Course.objects.count()
        context['total_results'] = models.Result.objects.count()
        context['current_semester'] = get_current_semester()
        
        # Get recent results
        context['recent_results'] = (
            models.Result.objects.select_related('student', 'course')
            .order_by('-recorded_at')[:5]
        )
        
        # Get top performers (students with highest GPAs)
        top_students = models.Student.objects.filter(is_active=True)
        top_students = sorted(
            [(student, student.calculate_gpa()) for student in top_students],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        context['top_performers'] = [student for student, _ in top_students]
        
        return context


class AdminSettingsUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Allow an admin to edit their own account info (first_name, last_name, email)."""
    model = User
    template_name = 'eturesultapp/admin_settings.html'
    fields = ['first_name', 'last_name', 'email']

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers (admins) to access this
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('eturesultapp:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # Edit the logged-in user's record
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('eturesultapp:dashboard_admin')


class AdminDeleteView(LoginRequiredMixin, generic.DeleteView):
    """Allow an admin to delete their own account after confirmation."""
    model = User
    template_name = 'eturesultapp/admin_delete_confirm.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('eturesultapp:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        # After deleting self, redirect to public home
        return reverse_lazy('eturesultapp:home')

