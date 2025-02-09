from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from user_auth.utils.decorators import requiere_almacenista


@csrf_protect
@requiere_almacenista
def inventoryRenderView(request):
    group_name = None

    # Make sure the user is authenticated and has a 'grupo'
    if request.user.is_authenticated and request.user.grupo:
        group_name = request.user.grupo.nombre

    # Now pass group_name to the template or use it directly here
    return render(request, 'inventario.html', {'group_name': group_name})
