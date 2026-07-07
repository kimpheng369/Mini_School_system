# core/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def role_required(role):
    """
    Decorator for views that checks that the user has a certain role.
    """
    def check_role(user):
        if user.is_authenticated and user.role == role:
            return True
        raise PermissionDenied
    return user_passes_test(check_role)

employee_required = role_required('EMPLOYEE')
instructor_required = role_required('INSTRUCTOR')
student_required = role_required('STUDENT')