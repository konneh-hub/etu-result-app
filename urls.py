from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from . import views, api

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'api/students', api.StudentViewSet)
router.register(r'api/courses', api.CourseViewSet)
router.register(r'api/results', api.ResultViewSet)

app_name = 'eturesultapp'

urlpatterns = [
    # Dashboard
    path('', views.home_view, name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='dashboard_admin'),
    path('dashboard/lecturer/', views.lecturer_dashboard_view, name='dashboard_lecturer'),
    path('dashboard/student/', views.student_dashboard_view, name='dashboard_student'),
    # Support legacy /dashboard/ URL by redirecting to the canonical dashboard at '/'
    path('dashboard/', RedirectView.as_view(pattern_name='eturesultapp:dashboard', permanent=False), name='dashboard_redirect'),
    
    # Registration
    path('register/student/', views.register_student_view, name='register_student'),
    path('register/lecturer/', views.register_lecturer_view, name='register_lecturer'),
    path('register/admin/', views.register_admin_view, name='register_admin'),
    path('register/complete/', views.registration_complete, name='registration_complete'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    # Admin settings (edit / delete own admin account)
    path('admin/settings/', views.AdminSettingsUpdateView.as_view(), name='admin_settings'),
    path('admin/settings/delete/', views.AdminDeleteView.as_view(), name='admin_delete'),
    
    # Lecturers
    path('lecturers/', views.LecturerListView.as_view(), name='lecturer_list'),
    path('lecturers/add/', views.LecturerCreateView.as_view(), name='lecturer_create'),
    path('lecturers/<int:pk>/', views.LecturerDetailView.as_view(), name='lecturer_detail'),
    path('lecturers/<int:pk>/edit/', views.LecturerUpdateView.as_view(), name='lecturer_update'),
    path('lecturers/<int:pk>/delete/', views.LecturerDeleteView.as_view(), name='lecturer_delete'),
    
    # Students
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/add/', views.StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_edit'),
    path('students/<int:pk>/edit-self/', views.StudentSelfUpdateView.as_view(), name='student_edit_self'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    path('students/<int:pk>/download/', views.student_results_download, name='student_download'),
    path('export/results/', views.export_all_results, name='export_results'),

    # API URLs
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),

    # Courses
    path('courses/', views.CourseListView.as_view(), name='course_list'),
        path('courses/add/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),

    # Results
    path('results/', views.ResultListView.as_view(), name='result_list'),
        path('results/add/', views.ResultCreateView.as_view(), name='result_create'),
    # Note: legacy names cleaned up; use 'result_create'
    path('results/<int:pk>/edit/', views.ResultUpdateView.as_view(), name='result_edit'),
    path('results/<int:pk>/delete/', views.ResultDeleteView.as_view(), name='result_delete'),
]
