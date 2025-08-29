import os
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from core.models import Company, Department
from django.conf import settings

LOG_FILE = os.path.join(settings.BASE_DIR, "logs", "app.log")

@pytest.fixture
def user(db, django_user_model):
    # مستخدم عادي للتصديقات
    return django_user_model.objects.create_user(
        username="user1",
        email="user1@example.com",
        password="123"
    )

@pytest.fixture
def clear_log_file():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.truncate(0)

@pytest.mark.django_db
def test_department_list_and_logs(user, clear_log_file):
    client = APIClient()
    client.force_authenticate(user=user)

    company = Company.objects.create(name="Comp A", company_slug="comp-a")
    Department.objects.create(name="Dept 1", department_slug="dept-1", company=company)
    Department.objects.create(name="Dept 2", department_slug="dept-2", company=company)

    url = reverse("department-list", kwargs={"company_slug": company.company_slug})
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("name" in d for d in data)

    with open(LOG_FILE) as f:
        logs = f.read().lower()
    assert "requested department list" in logs

@pytest.mark.django_db
def test_department_detail_and_logs(user, clear_log_file):
    client = APIClient()
    client.force_authenticate(user=user)

    company = Company.objects.create(name="Comp A", company_slug="comp-a")
    dept = Department.objects.create(name="Dept 1", department_slug="dept-1", company=company)

    url = reverse("department-detail", kwargs={
        "company_slug": company.company_slug,
        "department_slug": dept.department_slug
    })
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Dept 1"

    with open(LOG_FILE) as f:
        logs = f.read().lower()
    assert "requested department" in logs
