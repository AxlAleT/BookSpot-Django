from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login.html', permanent=True)),
    path('', include('user_auth.urls')),
    path('inventory/', include('inventory.urls')),
]