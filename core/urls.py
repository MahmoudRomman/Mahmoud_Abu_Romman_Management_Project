from django.urls import path
from . import views


urlpatterns = [
    # Company URLS
    path("companies/", views.company_list, name="company-list"),
    path("companies/<slug:company_slug>/", views.company_detail, name="company-detail"),

    # Department URLS
    path("companies/<slug:company_slug>/departments/", views.department_list, name="department-list"),
    path("companies/<slug:company_slug>/departments/<slug:department_slug>/", views.department_detail, name="department-detail"),

    # Employee URLS
    path("employees/", views.employee_list, name="employee-list"),
    path("employees/create/", views.employee_create, name="employee-create"),
    path("employees/<slug:employee_slug>/", views.employee_detail, name="employee-detail"),
    path("employees/<slug:employee_slug>/update/", views.employee_update, name="employee-update"),
    path("employees/<slug:employee_slug>/delete/", views.employee_delete, name="employee-delete"),

    # Project URLS
    path("projects/", views.project_list, name="project-list"),
    path("projects/create/", views.project_create, name="project-create"),
    path("projects/<slug:project_slug>/", views.project_detail, name="project-detail"),
    path("projects/<slug:project_slug>/update/", views.project_update, name="project-update"),
    path("projects/<slug:project_slug>/delete/", views.project_delete, name="project-delete"),


    # PerformanceReview URLs
    path("reviews/", views.review_create, name="review-create"), 
    path("reviews/<int:review_id>/", views.review_detail, name="review-detail"), 
    path("reviews/<int:review_id>/transition/", views.review_transition, name="review-transition"),  
    path("reviews/<int:review_id>/delete/", views.review_delete, name="review-delete"),  

]


