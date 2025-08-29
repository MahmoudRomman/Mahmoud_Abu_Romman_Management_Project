import logging
import os
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.conf import settings
from django.contrib.auth import get_user_model

# الـ log file path
LOG_FILE = os.path.join(settings.BASE_DIR, "logs", "app.log")

# استخدام logger من الـ core app
logger = logging.getLogger("core")


@pytest.mark.django_db
def test_company_list_logs_and_response():
    # نتأكد أن مجلد اللوج موجود
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    client = APIClient()

    # 👇 مستخدم superuser
    User = get_user_model()
    user = User.objects.create_superuser(email="superadmin@test.com", password="test1234")
    client.force_authenticate(user=user)

    url = reverse("company-list")
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # نضيف لوج مباشر
    logger = logging.getLogger("core")
    logger.info("requested company list")

    # نشيك أن الملف موجود (مش بنحذفه)
    assert os.path.exists(LOG_FILE), "Log file was not created"

    # ونتأكد أن الرسالة موجودة بالملف
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = f.read()
    assert "requested company list" in logs


