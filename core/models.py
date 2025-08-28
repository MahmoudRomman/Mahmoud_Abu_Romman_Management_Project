from django.db import models
from django.utils import timezone


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)

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

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    @property
    def num_employees(self):
        return self.employees.count()

    @property
    def num_projects(self):
        return self.projects.count()


class Employee(models.Model):
    company = models.ForeignKey(Company, related_name="employees", on_delete=models.CASCADE)
    department = models.ForeignKey(
        Department, related_name="employees", on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    designation = models.CharField(max_length=255)
    hired_on = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.company.name}"

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

    def __str__(self):
        return f"{self.name} ({self.company.name})"
