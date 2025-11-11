from rest_framework import viewsets
from rest_framework import filters
from .models import Student, Course, Result
from .serializers import StudentSerializer, CourseSerializer, ResultSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by('student_id')
    serializer_class = StudentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['student_id', 'first_name', 'last_name', 'email']

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('code')
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'name']

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all().select_related('student', 'course').order_by('-recorded_at')
    serializer_class = ResultSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['student__student_id', 'course__code', 'grade', 'semester']