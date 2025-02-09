# decorators.py
from django.http import JsonResponse
from functools import wraps


def requiere_grupo(grupo_requerido):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Acceso no autorizado. Por favor, inicie sesión."}, status=403)

            if not request.user.grupo:
                return JsonResponse({"error": "Acceso no autorizado. No se ha asignado un grupo al usuario."},
                                    status=403)

            # If user has 'admin' group, skip further checks
            if request.user.grupo.nombre == 'admin':
                return view_func(request, *args, **kwargs)

            # Otherwise, check if the user's group matches the required group
            if request.user.grupo.nombre != grupo_requerido:
                return JsonResponse({
                    "error": f"Acceso no autorizado para este grupo. Se requiere: {grupo_requerido}"
                }, status=403)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# Specific decorators
requiere_admin = requiere_grupo('Admin')
requiere_vendedor = requiere_grupo('Vendedor')
requiere_almacenista = requiere_grupo('Almacenista')