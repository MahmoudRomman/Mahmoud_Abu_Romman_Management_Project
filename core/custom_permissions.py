# core/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

COMPANY_ROLES = {"company_admin", "hr", "manager", "employee", "viewer"}

def user_company(user):
    try:
        return user.employee_profile.company
    except Exception:
        return None

def same_company(user, obj_company):
    uc = user_company(user)
    return uc is not None and obj_company is not None and uc.id == obj_company.id

def is_manager(user):
    return getattr(user, "role", None) == "manager"

def is_hr(user):
    return getattr(user, "role", None) == "hr"

def is_company_admin(user):
    return getattr(user, "role", None) == "company_admin"

def is_super(user):
    return getattr(user, "role", None) == "superadmin" or getattr(user, "is_superuser", False)

def is_company_role(user):
    return getattr(user, "role", None) in COMPANY_ROLES or is_super(user)


class IsAuthenticatedActive(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.is_active)


class RolePermission(BasePermission):
    allowed_roles = set()
    allow_super = True

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_active):
            return False
        if self.allow_super and is_super(user):
            return True
        return getattr(user, "role", None) in self.allowed_roles


class IsSuperOrCompanyAdmin(RolePermission):
    allowed_roles = {"company_admin"}
    allow_super = True


class IsHRorCompanyAdminOrSuper(RolePermission):
    allowed_roles = {"hr", "company_admin"}
    allow_super = True


class IsManagerOrAbove(RolePermission):
    allowed_roles = {"manager", "company_admin", "hr"} 
    allow_super = True


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS



class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_superuser or getattr(request.user, "role", None) == "company_admin"



class IsSameCompanyObject(BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_super(request.user):
            return True
        obj_company = getattr(obj, "company", None)
        return same_company(request.user, obj_company)


class EmployeeObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        u = request.user
        if is_super(u):
            return True

        employee = obj
        obj_company = employee.company
        if not same_company(u, obj_company):
            return False

        role = getattr(u, "role", None)
        if request.method in SAFE_METHODS:
            if role in {"company_admin", "hr"}:
                return True
            if role == "manager":
                try:
                    return u.employee_profile.department_id == employee.department_id
                except Exception:
                    return False
            if role == "employee":
                try:
                    return getattr(u, "employee_profile", None) and u.employee_profile.id == employee.id
                except Exception:
                    return False
            return False

        # write operations
        if role in {"company_admin", "hr"}:
            return True

        if role == "employee":
            try:
                return getattr(u, "employee_profile", None) and u.employee_profile.id == employee.id
            except Exception:
                return False

        return False


class ProjectObjectPermission(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if is_super(user):
            return True

        obj_company = obj.company
        if not same_company(user, obj_company):
            return False

        role = getattr(user, "role", None)
        if request.method in SAFE_METHODS:
            return is_company_role(user)

        if role == "company_admin":
            return True
        if role == "manager":
            try:
                return user.employee_profile.department_id == obj.department_id
            except Exception:
                return False

        return False



# target_stage: "SCHEDULED" / "FEEDBACK" / "UNDER_APPROVAL" / "APPROVED" / "REJECTED"
def can_transition(user, review, target_stage):
    if not (is_super(user) or same_company(user, review.employee.company)):
        return False, "Not same company."

    role = getattr(user, "role", None)

    if target_stage == "SCHEDULED":  # Pending -> Scheduled
        if is_super(user) or is_company_admin(user) or is_hr(user) or is_manager(user):
            return True, None
        return False, "Only manager/HR/admin can schedule."

    if target_stage == "FEEDBACK":   # Scheduled -> Feedback OR Rejected -> Feedback
        if is_super(user) or is_company_admin(user) or is_hr(user) or is_manager(user):
            return True, None
        try:
            if user.employee_profile.id == review.employee_id:
                return True, None
        except Exception:
            pass
        return False, "Only employee/reviewer/manager/HR/admin can provide feedback."

    if target_stage == "UNDER_APPROVAL":  # Feedback -> Under Approval
        if is_super(user) or is_company_admin(user) or is_hr(user) or is_manager(user):
            return True, None
        try:
            if user.employee_profile.id == review.employee_id:
                return True, None
        except Exception:
            pass
        return False, "Not allowed to submit for approval."

    if target_stage in {"APPROVED", "REJECTED"}:  # Under Approval -> Approved/Rejected
        if is_super(user) or is_company_admin(user) or is_manager(user):
            return True, None
        return False, "Only manager or admin can approve/reject."

    return False, "Unknown target stage."
