from django.db import models
from django.utils import timezone
from accounts.models import User
import random



def generate_unique_slug(custom_model):
    while True:
        slug = str(random.randint(10000000, 99999999))  
        if not custom_model.objects.filter(slug=slug).exists():
            return slug



class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    company_slug = models.SlugField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        if not self.company_slug:
            self.company_slug = generate_unique_slug(Company)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def num_departments(self):
        return self.departments.count()

    @property
    def num_employees(self):
        return self.employees.count()

    @property
    def num_projects(self):
        return self.projects.count()




class Department(models.Model):
    company = models.ForeignKey(Company, related_name="departments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    department_slug = models.SlugField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        if not self.department_slug:
            self.department_slug = generate_unique_slug(Department)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    @property
    def num_employees(self):
        return self.employees.count()

    @property
    def num_projects(self):
        return self.projects.count()


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")
    company = models.ForeignKey(Company, related_name="employees", on_delete=models.CASCADE)
    department = models.ForeignKey(
        Department, related_name="employees", on_delete=models.SET_NULL, null=True, blank=True
    )
    designation = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    hired_on = models.DateField(null=True, blank=True)
    employee_slug = models.SlugField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        if not self.employee_slug:
            self.employee_slug = generate_unique_slug(Employee)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    def __str__(self):
        return f"{self.user.email} - {self.company.name}"

    @property
    def days_employed(self):
        if self.hired_on:
            return (timezone.now().date() - self.hired_on).days
        return None


class Project(models.Model):
    company = models.ForeignKey(Company, related_name="projects", on_delete=models.CASCADE)
    department = models.ForeignKey(
        Department, related_name="projects", on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    assigned_employees = models.ManyToManyField(Employee, related_name="projects", blank=True)
    project_slug = models.SlugField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        if not self.project_slug:
            self.project_slug = generate_unique_slug(Project)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class PerformanceReview(models.Model):
    STAGES = [
        ("PENDING", "Pending Review"),
        ("SCHEDULED", "Review Scheduled"),
        ("FEEDBACK", "Feedback Provided"),
        ("UNDER_APPROVAL", "Under Approval"),
        ("APPROVED", "Review Approved"),
        ("REJECTED", "Review Rejected"),
    ]

    employee = models.ForeignKey(Employee, related_name="reviews", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(
        Employee, related_name="reviews_given", on_delete=models.SET_NULL, null=True, blank=True
    )
    manager = models.ForeignKey(
        Employee, related_name="reviews_to_approve", on_delete=models.SET_NULL, null=True, blank=True
    )

    stage = models.CharField(max_length=20, choices=STAGES, default="PENDING")
    feedback = models.TextField(blank=True)
    scheduled_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.employee.name} ({self.get_stage_display()})"
