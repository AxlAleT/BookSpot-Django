
from .api.views import *
from django.urls import path


urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/libros/', obtener_libros, name='obtener_libros'),
    path('login/', login_view, name='login'),
]