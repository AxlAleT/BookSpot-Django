# permissions.py
from rest_framework import permissions


class GrupoPermission(permissions.BasePermission):
    """
    Custom permission to check if the user belongs to a specific group,
    with admin having unrestricted access.
    """

    def has_permission(self, request, view):
        grupo_requerido = getattr(view, 'grupo_requerido', None)

        # Check if user is authenticated and has a group
        if not request.user.is_authenticated or not request.user.grupo:
            return False

        # If the user is admin, always allow
        if request.user.grupo.nombre == 'admin':
            return True

        # Otherwise require matching group
        return request.user.grupo.nombre == grupo_requerido