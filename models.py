from django.db import models
from django.contrib.auth.models import User


class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    is_admin_assistant = models.BooleanField(default=False)
    courses = models.ManyToManyField('Course', related_name='lecturers', blank=True)

    def __str__(self):
        return f"{self.staff_id} - {self.user.get_full_name()}"

    class Meta:
        permissions = [
            ("can_manage_results", "Can manage course results"),
        ]


class Student(models.Model):
    # Optional link to Django User for stronger identity mapping
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    program = models.CharField(max_length=128, blank=True, null=True)
    department = models.CharField(max_length=128, blank=True, null=True)
    faculty = models.CharField(max_length=128, blank=True, null=True)
    enrollment_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['student_id', 'last_name', 'first_name']

    def __str__(self) -> str:
        return f"{self.student_id} - {self.last_name}, {self.first_name}"

    def calculate_gpa(self):
        grades = self.results.all()
        if not grades:
            return 0.0
        grade_points = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D': 1.0, 'F': 0.0
        }
        total_points = sum(grade_points.get(g.grade, 0) * g.course.credits for g in grades)
        total_credits = sum(g.course.credits for g in grades)
        return round(total_points / total_credits, 2) if total_credits else 0.0


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    credits = models.PositiveSmallIntegerField(default=3)
    description = models.TextField(blank=True)
    semester = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Result(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'),
        ('D', 'D'), ('F', 'F'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='results')
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES)
    semester = models.CharField(max_length=32, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, help_text="Any additional notes about this result")

    class Meta:
        unique_together = ('student', 'course', 'semester')
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['student', 'semester']),
            models.Index(fields=['course', 'semester']),
            models.Index(fields=['grade']),
        ]

    def __str__(self) -> str:
        return f"{self.student} | {self.course} : {self.grade} ({self.semester})"
        
    def get_grade_points(self):
        grade_points = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D': 1.0, 'F': 0.0
        }
        return grade_points.get(self.grade, 0)
