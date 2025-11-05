from accounts.models import AdminUser
from rest_framework import permissions


class IsPatientUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, AdminUser)
