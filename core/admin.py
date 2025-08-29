from django.contrib import admin
from .models import Company, Department, Employee, Project, PerformanceReview


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "num_departments", "num_employees", "num_projects")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "num_employees", "num_projects")

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("get_name", "get_email", "get_role", "department", "company", "designation")

    def get_name(self, obj):
        return obj.user.username or obj.user.email
    get_name.short_description = "Name"

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"

    def get_role(self, obj):
        return obj.user.role
    get_role.short_description = "Role"

    list_filter = ("department", "company", "designation")






@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "department", "start_date", "end_date")
    filter_horizontal = ("assigned_employees",)


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ("employee", "reviewer", "manager", "stage", "scheduled_date", "created_at", "updated_at")
    list_filter = ("stage", "scheduled_date", "created_at")
    search_fields = ("employee__name", "reviewer__name", "manager__name")
