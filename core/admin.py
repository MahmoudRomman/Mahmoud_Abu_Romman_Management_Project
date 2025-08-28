from django.contrib import admin
from .models import Company, Department, Employee, Project


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "num_departments", "num_employees", "num_projects")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "num_employees", "num_projects")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "department", "designation", "email", "days_employed")
    search_fields = ("name", "email", "designation")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "department", "start_date", "end_date")
    filter_horizontal = ("assigned_employees",)
