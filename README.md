# Mahmoud_Abu_Romman_Management_Project
This is a task to make a management system for a certain company (you can think of it as small ERP System)




## Strart the project

powershell
# create an environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# install all the requirements
pip install -r requirements.txt

# Starting the database
python manage.py makemigrations
python manage.py migrate

# Runngin the server
python manage.py runserver

---------------------------------------------------------------------------


## Used-Techs

- Python 3.11+
- Django 4.x
- Django REST Framework
- JWT
- SQLite 
- Logging 
- Role-based permissions

---------------------------------------------------------------------------

## Models
- accounts app:
**User**
  - email
  - username
  - role
  - Has the property ==> is_admin


- core app:
1. **Company**
   - name
   - company_slug
   - relations: departments, employees, projects

2. **Department**
   - name
   - department_slug
   - FK with Company
   - relations: employees, projects

3. **Employee**
   - FK with User, Company, وDepartment
   - designation, address, hired_on, employee_slug
   - Has ManyToMany relation with Projects
   - Has the property ==> days_employed

4. **Project**
   - FK with Company وDepartment
   - name, description, start_date, end_date, project_slug
   - Has ManyToMany with Employees

5. **PerformanceReview**
   - FK with Employee, reviewer, وmanager
   - stage (Pending, Scheduled, Feedback, Under Approval, Approved, Rejected)
   - feedback, scheduled_date, created_at, updated_at

---------------------------------------------------------------------------

## Serializers

- account app:
  - class RegisterSerializer
  - LoginSerializer

- core app:
  * Each model has its own dedicated Serializer:
  - CompanySerializer
  - DepartmentSerializer
  - EmployeeSerializer
  - ProjectSerializer
  - PerformanceReviewSerializer

---------------------------------------------------------------------------

## Views
- account app:
  - register
  - login
  - logout


- core app:
  - **Company Views**
    - company_list 
    - company_detail 

  - **Department Views**
    - department_list
    - department_detail

  - **Employee Views**
    - employee_list 
    - employee_create 
    - employee_detail 
    - employee_update
    - employee_delete

  - **Project Views**
    - project_list 
    - project_create
    - project_detail
    - project_update 
    - project_delete

  - **PerformanceReview Views**
    - review_create
    - review_detail
    - review_transition
    - review_delete

---------------------------------------------------------------------------

## URLs

### accounts
| Method | URL | Description |
|--------|-----|------------|
| GET    | /auth/register/ | register |
| GET    | /auth/login/    | login    |
| GET    | /auth/logout/    | logout    |


### Companies
| Method | URL | Description |
|--------|-----|------------|
| POST   | /companies/ | company_list |
| POST   | /companies/<slug:company_slug>/ | company_detail |




### Departments
| Method | URL | Description |
|--------|-----|------------|
| GET    | /companies/<slug:company_slug>/departments/ | department_list |
| GET    | /companies/<slug:company_slug>/departments/<slug:department_slug>/ | department_detail |



### Employees
| Method | URL | Description |
|--------|-----|------------|
| GET    | /employees/ | employee_list |
| POST   | /employees/create/ | employee_create |
| GET    | /employees/<slug:employee_slug>/ | employee_detail |
| PATCH  | /employees/<slug:employee_slug>/update/ | employee_update |
| DELETE | /employees/<slug:employee_slug>/delete/ | employee_delete |



### Projects
| Method | URL | Description |
|--------|-----|------------|
| GET    | /projects/ | project_list |
| POST   | /projects/create/ | project_create |
| GET    | /projects/<slug:project_slug>/ | project_detail |
| PATCH  | /projects/<slug:project_slug>/update/ | project_update |
| DELETE | /projects/<slug:project_slug>/delete/ | project_delete |



### Performance Reviews
| Method | URL | Description |
|--------|-----|------------|
| POST   | /reviews/ | review_create |
| GET    | /reviews/<int:review_id>/ | review_detail |
| PATCH  | /reviews/<int:review_id>/transition/ | review_transition |
| DELETE | /reviews/<int:review_id>/delete/ | review_delete |

---------------------------------------------------------------------------


## Permissions 

- **Roles**: superadmin, company_admin, hr, manager, employee, viewer
---------------------------------------------------------------------------

## Logging
- specific logging for each action
    - info for successful operations
    - warning for unauthorized access or failures
    - error for internal errors
    
---------------------------------------------------------------------------


