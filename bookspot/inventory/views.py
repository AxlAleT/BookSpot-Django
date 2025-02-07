from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from user_auth.utils.decorators import requiere_almacenista


@csrf_protect
@requiere_almacenista
def inventoryRenderView(request):
    return render(request, 'inventario.html')