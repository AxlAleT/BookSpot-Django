from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from user_auth.utils.decorators import requiere_vendedor


@csrf_protect
@requiere_vendedor
def salesRenderView(request):

    group_name = request.user.grupo.nombre
    return render(request, 'sales.html', {'group_name': group_name})
