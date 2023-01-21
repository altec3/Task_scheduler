from rest_framework.permissions import BasePermission


class IsOwnerOrStaff(BasePermission):
    message = "Delete or edit categories can owners or admins only."

    def has_object_permission(self, request, view, obj):
        if request.user == obj.user or request.user.is_staff:
            return True
        return False
