from django.http import JsonResponse
from functools import wraps


def requiere_grupo(grupo_requerido):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Acceso no autorizado. Por favor, inicie sesión."}, status=403)

            if not request.user.grupo or request.user.grupo.nombre != grupo_requerido:
                return JsonResponse({"error": f"Acceso no autorizado para este grupo. Se requiere: {grupo_requerido}"},
                                    status=403)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# Specific decorators
requiere_admin = requiere_grupo('admin')
requiere_vendedor = requiere_grupo('vendedor')
requiere_almacenista = requiere_grupo('almacenista')