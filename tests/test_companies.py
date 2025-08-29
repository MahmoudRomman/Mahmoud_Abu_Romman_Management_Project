import os
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from core.models import Company
from django.conf import settings

LOG_FILE = os.path.join(settings.BASE_DIR, "logs", "app.log")

@pytest.mark.django_db
def test_company_list_logs_and_response():
    client = APIClient()

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    # تفريغ الملف بدل الحذف
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.truncate(0)

    Company.objects.create(name="Comp A", company_slug="comp-a")
    Company.objects.create(name="Comp B", company_slug="comp-b")

    url = reverse("company-list")
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("name" in c for c in data)

    with open(LOG_FILE) as f:
        logs = f.read().lower()
    assert "requested company list" in logs


@pytest.mark.django_db
def test_company_detail_logs_and_response():
    client = APIClient()

    company = Company.objects.create(name="Comp A", company_slug="comp-a")

    url = reverse("company-detail", kwargs={"company_slug": company.company_slug})
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    # نتحقق من الاسم بدل company_slug
    assert data["name"] == "Comp A"

    with open(LOG_FILE) as f:
        logs = f.read().lower()
    assert "requested details for company" in logs
