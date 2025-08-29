from rest_framework import serializers
from .models import Company, Department, Employee, Project, PerformanceReview

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["name", "num_departments", "num_employees", "num_projects"]
        read_only_fields = ["num_departments", "num_employees", "num_projects"]





class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["name", "num_employees", "num_projects"]
        read_only_fields = ["num_employees", "num_projects"]


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        exclude = ("employee_slug",) 



class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ("project_slug",) 



class PerformanceReviewSerializer(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source='employee', write_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source='reviewer', required=False, allow_null=True)
    manager_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source='manager', required=False, allow_null=True)

    class Meta:
        model = PerformanceReview
        fields = [
            "id",
            "employee_id",
            "reviewer_id",
            "manager_id",
            "stage",
            "feedback",
            "scheduled_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "stage"]  # stage يتم التحكم فيه من view transition
