from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def inventoryRenderView(request):
    return render(request, 'inventario.html')