from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Company, Department, Employee, Project, PerformanceReview
from .serializers import CompanySerializer, DepartmentSerializer, EmployeeSerializer, ProjectSerializer, PerformanceReviewSerializer
from .custom_permissions import IsAdminOrReadOnly, EmployeeObjectPermission, IsAuthenticatedActive, can_transition
from django.core.exceptions import ObjectDoesNotExist
import logging


logger = logging.getLogger(__name__)  

# ======================= Companies Actions ======================= 
# get all companies 
@api_view(["GET"])
@permission_classes([IsAdminOrReadOnly])
def company_list(request):
    logger.info(f"User {request.user} requested company list")
    companies = Company.objects.all()
    serializer = CompanySerializer(companies, many=True)
    logger.debug(f"Returning {len(companies)} companies")
    return Response(serializer.data, status=status.HTTP_200_OK)





# get a single company by its slug
@api_view(["GET"])
@permission_classes([IsAdminOrReadOnly])
def company_detail(request, company_slug):
    logger.info(f"User {request.user} requested details for company {company_slug}")
    try:
        company = Company.objects.get(company_slug=company_slug)
    except Company.DoesNotExist:
        logger.warning(f"Company with slug {company_slug} not found")
        return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CompanySerializer(company)
    logger.debug(f"Returning details for company {company_slug}")
    return Response(serializer.data, status=status.HTTP_200_OK)





# ======================= Departments Actions ======================= 
# get all departments inside a company
@api_view(["GET"])
def department_list(request, company_slug):
    logger.info(f"User {request.user} requested department list for company {company_slug}")
    try:
        company = Company.objects.get(company_slug=company_slug)  
    except ObjectDoesNotExist:
        logger.warning(f"Company with slug {company_slug} not found while fetching departments")
        return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

    departments = Department.objects.filter(company=company)
    serializer = DepartmentSerializer(departments, many=True)   
    logger.debug(f"Returning {len(departments)} departments for company {company_slug}")
    return Response(serializer.data, status=status.HTTP_200_OK)


# get a single department inside a certain company
@api_view(["GET"])
def department_detail(request, company_slug, department_slug):
    logger.info(f"User {request.user} requested department {department_slug} in company {company_slug}")
    try:
        company = Company.objects.get(company_slug=company_slug) 
    except ObjectDoesNotExist:
        logger.warning(f"Company with slug {company_slug} not found while fetching department {department_slug}")
        return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        department = Department.objects.get(company=company, department_slug=department_slug) 
    except ObjectDoesNotExist:
        logger.warning(f"Department {department_slug} not found in company {company_slug}")
        return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = DepartmentSerializer(department)
    logger.debug(f"Returning details for department {department_slug} in company {company_slug}")
    return Response(serializer.data, status=status.HTTP_200_OK)




# ======================= Employees Actions ======================= 

# get the employee list for a certian company
@api_view(["GET"])
@permission_classes([IsAuthenticatedActive])
def employee_list(request):
    user = request.user
    try:
        if user.role == "superadmin" or user.is_superuser:
            employees = Employee.objects.all()
            logger.info(f"[{user}] fetched all employees (superadmin).")

        elif user.role in ["company_admin", "hr"]:
            employees = Employee.objects.filter(company=user.employee_profile.company)
            logger.info(f"[{user}] fetched employees for company {user.employee_profile.company}.")

        elif user.role == "manager":
            employees = Employee.objects.filter(
                company=user.employee_profile.company,
                department=user.employee_profile.department
            )
            logger.info(f"[{user}] fetched employees for department {user.employee_profile.department}.")
        else:
            logger.warning(f"[{user}] tried to fetch employees but not allowed.")
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error fetching employee list by [{user}]: {str(e)}")
        return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# get details for a certian employee
@api_view(["GET"])
@permission_classes([IsAuthenticatedActive, EmployeeObjectPermission])
def employee_detail(request, employee_slug):
    user = request.user
    try:
        employee = get_object_or_404(Employee, employee_slug=employee_slug)
        logger.info(f"[{user}] viewed details for employee {employee}.")

        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error fetching employee {employee_slug} details by [{user}]: {str(e)}")
        return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# create a new employee
@api_view(["POST"])
@permission_classes([IsAuthenticatedActive])
def employee_create(request):
    user = request.user
    if not (user.role in ["company_admin", "hr"] or user.is_superuser):
        logger.warning(f"[{user}] tried to create employee but not allowed.")
        return Response({"detail": "Not allowed to create employee."}, status=status.HTTP_403_FORBIDDEN)

    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        if Employee.objects.filter(user=serializer.validated_data["user"]).exists():
            logger.warning(f"[{user}] tried to create duplicate employee for user {serializer.validated_data['user']}.")
            return Response(
                {"detail": "This user already has an employee profile."},
                status=status.HTTP_400_BAD_REQUEST
            )

        employee = serializer.save(company=user.employee_profile.company)
        logger.info(f"[{user}] created new employee {employee}.")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.warning(f"[{user}] failed to create employee due to validation errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# update the data for a certain employee
@api_view(["PATCH"])
@permission_classes([IsAuthenticatedActive, EmployeeObjectPermission])
def employee_update(request, employee_slug):
    user = request.user
    employee = get_object_or_404(Employee, employee_slug=employee_slug)

    if user.role in ["superadmin", "company_admin", "hr"] or user.is_superuser:
        logger.info(f"[{user}] updating employee {employee}.")
    elif user.role == "employee" and employee == user.employee_profile:
        allowed = {"address", "phone_number"}
        for field in request.data.keys():
            if field not in allowed:
                logger.warning(f"[{user}] tried to update forbidden field '{field}' in {employee}.")
                return Response(
                    {"detail": f"Employees can only update {allowed}."},
                    status=status.HTTP_403_FORBIDDEN
                )
        logger.info(f"[{user}] updated personal data for {employee}.")
    else:
        logger.warning(f"[{user}] tried to update employee {employee} but not allowed.")
        return Response({"detail": "Not allowed to update."}, status=status.HTTP_403_FORBIDDEN)

    serializer = EmployeeSerializer(employee, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.warning(f"[{user}] failed to update {employee} due to validation errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# delete an employee
@api_view(["DELETE"])
@permission_classes([IsAuthenticatedActive, EmployeeObjectPermission])
def employee_delete(request, employee_slug):
    user = request.user
    employee = get_object_or_404(Employee, employee_slug=employee_slug)

    if not (user.role == "company_admin" or user.is_superuser):
        logger.warning(f"[{user}] tried to delete {employee} but not allowed.")
        return Response({"detail": "Not allowed to delete."}, status=status.HTTP_403_FORBIDDEN)

    employee.delete()
    logger.info(f"[{user}] deleted employee {employee}.")
    return Response(status=status.HTTP_204_NO_CONTENT)




# ======================= Project Actions ======================= 

@api_view(["GET"])
def project_list(request):
    """Retrieve all projects"""
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    logger.info("Retrieved list of projects, count=%s", len(projects))
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def project_create(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        logger.info("Created new project: %s", serializer.data.get("name"))
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    logger.error("Project creation failed: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def project_detail(request, project_slug):
    try:
        project = Project.objects.get(project_slug=project_slug)
    except Project.DoesNotExist:
        logger.warning("Project not found: slug=%s", project_slug)
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProjectSerializer(project)
    logger.info("Retrieved project: %s", project_slug)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
def project_update(request, project_slug):
    try:
        project = Project.objects.get(project_slug=project_slug)
    except Project.DoesNotExist:
        logger.warning("Project not found for update: slug=%s", project_slug)
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProjectSerializer(project, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info("Updated project: %s", project_slug)
        return Response(serializer.data, status=status.HTTP_200_OK)
    logger.error("Project update failed for slug=%s: %s", project_slug, serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def project_delete(request, project_slug):
    try:
        project = Project.objects.get(project_slug=project_slug)
    except Project.DoesNotExist:
        logger.warning("Project not found for delete: slug=%s", project_slug)
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

    project.delete()
    logger.info("Deleted project: %s", project_slug)
    return Response(status=status.HTTP_204_NO_CONTENT)




# ======================= PerformanceReview Actions ======================= 

@api_view(["POST"])
@permission_classes([IsAuthenticatedActive])
def review_create(request):
    serializer = PerformanceReviewSerializer(data=request.data)
    if serializer.is_valid():
        review = serializer.save(stage="PENDING") 
        logger.info("Created review %s for employee %s", review.id, review.employee_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    logger.error("Review creation failed: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([IsAuthenticatedActive])
def review_transition(request, review_id):
    try:
        review = PerformanceReview.objects.get(id=review_id)
    except PerformanceReview.DoesNotExist:
        return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

    target_stage = request.data.get("target_stage")
    if not target_stage:
        return Response({"error": "target_stage is required"}, status=status.HTTP_400_BAD_REQUEST)

    allowed, reason = can_transition(request.user, review, target_stage)
    if not allowed:
        return Response({"error": reason}, status=status.HTTP_403_FORBIDDEN)

    review.stage = target_stage
    if "feedback" in request.data:
        review.feedback = request.data["feedback"]
    if "scheduled_date" in request.data:
        review.scheduled_date = request.data["scheduled_date"]

    review.save()
    logger.info("Review %s transitioned to %s by user %s", review.id, target_stage, request.user.id)
    serializer = PerformanceReviewSerializer(review)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticatedActive])
def review_detail(request, review_id):
    try:
        review = PerformanceReview.objects.get(id=review_id)
    except PerformanceReview.DoesNotExist:
        return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = PerformanceReviewSerializer(review)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticatedActive])
def review_delete(request, review_id):
    try:
        review = PerformanceReview.objects.get(id=review_id)
    except PerformanceReview.DoesNotExist:
        return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

    review.delete()
    logger.info("Deleted review %s", review_id)
    return Response(status=status.HTTP_204_NO_CONTENT)
