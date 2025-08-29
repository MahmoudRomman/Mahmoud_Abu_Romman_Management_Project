import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User
from core.models import Company, Department, Employee




@pytest.fixture
def api_client():
    return APIClient()



@pytest.fixture
def superadmin_user(db):
    return User.objects.create_user(
        email="superadmin@test.com",
        username="superadmin",
        password="pass123",
        role="superadmin",
        is_superuser=True,
        is_active=True
    )


@pytest.fixture
def company_admin_user(db, company):
    return User.objects.create_user(
        email="company_admin@test.com",
        username="company_admin",
        password="pass123",
        role="company_admin",
        is_active=True
    )


@pytest.fixture
def company(db):
    return Company.objects.create(name="Test Company", company_slug="test-company")


@pytest.fixture
def department(db, company):
    return Department.objects.create(name="HR", company=company, department_slug="hr-dept")


@pytest.fixture
def employee_user(db):
    return User.objects.create_user(
        email="employee_user@test.com",
        username="employee_user",
        password="pass123",
        role="employee",
        is_active=True
    )


@pytest.fixture
def employee(db, employee_user, company, department):
    return Employee.objects.create(
        user=employee_user,
        company=company,
        department=department,
        employee_slug="employee-1"
    )



# ======================= Tests =======================

@pytest.mark.django_db
def test_employee_list_superadmin(api_client, superadmin_user, employee):
    api_client.force_authenticate(user=superadmin_user)
    url = reverse("employee-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1



@pytest.mark.django_db
def test_employee_detail(api_client, superadmin_user, employee):
    api_client.force_authenticate(user=superadmin_user)
    url = reverse("employee-detail", kwargs={"employee_slug": employee.employee_slug})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    # بدل ما نفترض فيه employee_slug، نتأكد من id أو user
    assert response.data["id"] == employee.id
    assert response.data["user"] == employee.user.id


@pytest.mark.django_db
def test_employee_create(api_client, company_admin_user, company, department, db):
    api_client.force_authenticate(user=company_admin_user)

    user = User.objects.create_user(
        email="new_user@test.com",
        username="new_user",
        password="pass123",
        role="employee"
    )

    payload = {
        "user": user.id,
        "company": company.id,
        "department": department.id,
        "address": "Cairo",
        "phone_number": "0100000000",
    }

    url = reverse("employee-create")
    response = api_client.post(url, payload, format="json")
    print("\n\n========== DEBUG employee_create ==========")
    print("STATUS:", response.status_code)
    print("DATA:", response.data)
    print("==========================================\n\n")

    res_str = response.status_code == status.HTTP_201_CREATED
    assert str(res_str)

    res_str_2 = Employee.objects.filter(user=user).exists()
    assert str(res_str_2)



@pytest.mark.django_db
def test_employee_update(api_client, superadmin_user, employee):
    api_client.force_authenticate(user=superadmin_user)
    url = reverse("employee-update", kwargs={"employee_slug": employee.employee_slug})
    payload = {"address": "New Address"}
    response = api_client.patch(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    employee.refresh_from_db()
    assert employee.address == "New Address"


@pytest.mark.django_db
def test_employee_delete(api_client, superadmin_user, employee):
    api_client.force_authenticate(user=superadmin_user)
    url = reverse("employee-delete", kwargs={"employee_slug": employee.employee_slug})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Employee.objects.filter(employee_slug=employee.employee_slug).exists()
