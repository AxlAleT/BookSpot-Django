from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

# Create your views here.

@csrf_protect
def loginRenderView(request):
    return render(request, 'login/login.html')