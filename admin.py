from django.contrib import admin
from . import models

# Brand the admin
admin.site.site_header = "Eastern Technical University"
admin.site.site_title = "ETU Admin"
admin.site.index_title = "Administration"


class ResultInline(admin.TabularInline):
	model = models.Result
	extra = 0
	readonly_fields = ('recorded_at',)


@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'email', 'user', 'enrollment_date', 'get_gpa')
    list_filter = ('enrollment_date', 'results__course__code')
    search_fields = ('student_id', 'first_name', 'last_name', 'email')
    ordering = ('-enrollment_date', 'student_id')
    date_hierarchy = 'enrollment_date'
    inlines = (ResultInline,)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student_id', 'first_name', 'last_name', 'email', 'user')
        }),
        ('Enrollment Details', {
            'fields': ('enrollment_date', 'is_active'),
            'classes': ('collapse',)
        })
    )
    
    def get_gpa(self, obj):
        grades = obj.results.all()
        if not grades:
            return 'N/A'
        grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
        total_points = sum(grade_points.get(g.grade, 0) * g.course.credits for g in grades)
        total_credits = sum(g.course.credits for g in grades)
        return f"{total_points / total_credits:.2f}" if total_credits else 'N/A'
    get_gpa.short_description = 'GPA'

    actions = ['mark_inactive', 'export_as_csv']
    # Admin actions
    actions += ['link_users_by_email']
    
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
    mark_inactive.short_description = "Mark selected students as inactive"
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        fieldnames = ['student_id', 'first_name', 'last_name', 'email', 'enrollment_date', 'is_active']
        # ensure Excel/Excel-like programs open UTF-8 correctly by adding BOM and charset
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=students_export.csv'
        response.write('\ufeff')  # UTF-8 BOM

        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        for student in queryset.select_related():
            writer.writerow({
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email or '',
                'enrollment_date': student.enrollment_date.isoformat() if student.enrollment_date else '',
                'is_active': student.is_active,
            })
        return response
    export_as_csv.short_description = "Export selected students to CSV"
    
    def link_users_by_email(self, request, queryset):
        """Admin action: link Student.user to User by matching email (case-insensitive).
        Skips students with no email or ambiguous matches.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        matched = 0
        skipped = 0
        ambiguous = 0
        for student in queryset:
            if student.user:
                # already linked
                continue
            if not student.email:
                skipped += 1
                continue
            try:
                user = User.objects.get(email__iexact=student.email)
            except User.DoesNotExist:
                skipped += 1
                continue
            except User.MultipleObjectsReturned:
                ambiguous += 1
                continue
            student.user = user
            student.save()
            matched += 1
        self.message_user(request, f"Linked {matched} students. Skipped {skipped}. Ambiguous: {ambiguous}")
    link_users_by_email.short_description = 'Link selected students to users by email'


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits', 'get_enrolled_count')
    list_filter = ('credits',)
    search_fields = ('code', 'name')
    ordering = ('code',)
    
    def get_enrolled_count(self, obj):
        return obj.results.count()
    get_enrolled_count.short_description = 'Enrolled Students'


@admin.register(models.Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'grade', 'semester', 'recorded_at', 'get_grade_status')
    list_filter = ('grade', 'semester', 'course', 'recorded_at')
    search_fields = ('student__student_id', 'student__first_name', 'student__last_name', 'course__code')
    date_hierarchy = 'recorded_at'
    
    fieldsets = (
        ('Result Information', {
            'fields': ('student', 'course', 'grade', 'semester')
        }),
        ('Additional Information', {
            'fields': ('remarks', 'recorded_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_grade_status(self, obj):
        if obj.grade in ['A', 'B', 'C']:
            return '✓ Pass'
        elif obj.grade == 'D':
            return '⚠ Conditional Pass'
        return '✗ Fail'
    get_grade_status.short_description = 'Status'
    
    actions = ['export_results', 'recalculate_gpas']
    
    def export_results(self, request, queryset):
        import csv
        from django.http import HttpResponse

        fieldnames = ['student_id', 'student_name', 'course_code', 'course_name', 'grade', 'semester', 'recorded_at', 'remarks']
        # ensure Excel/Excel-like programs open UTF-8 correctly by adding BOM and charset
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=results_export.csv'
        response.write('\ufeff')  # UTF-8 BOM

        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        for r in queryset.select_related('student', 'course'):
            writer.writerow({
                'student_id': r.student.student_id,
                'student_name': f"{r.student.first_name} {r.student.last_name}",
                'course_code': r.course.code,
                'course_name': r.course.name,
                'grade': r.grade,
                'semester': r.semester,
                'recorded_at': r.recorded_at.isoformat(),
                'remarks': r.remarks or '',
            })
        return response
    export_results.short_description = "Export selected results"
    
    def recalculate_gpas(self, request, queryset):
        students = set(result.student for result in queryset)
        for student in students:
            # GPA calculation will be triggered on save
            student.save()
        self.message_user(request, f"Recalculated GPAs for {len(students)} students")
    recalculate_gpas.short_description = "Recalculate GPAs"
