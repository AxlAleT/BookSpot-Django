# permissions.py
from rest_framework import permissions

class GrupoPermission(permissions.BasePermission):
    """
    Custom permission to check if the user belongs to a specific group.
    """

    def has_permission(self, request, view):
        # Get the required group from the view
        grupo_requerido = getattr(view, 'grupo_requerido', None)

        # Check if the user is authenticated and belongs to the required group
        return (
            request.user.is_authenticated and
            request.user.grupo and
            request.user.grupo.nombre == grupo_requerido
        )