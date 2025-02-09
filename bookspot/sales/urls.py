from django.urls import path
from .views import *
from .api.views import *

urlpatterns = [
    path('sales.html', salesRenderView),
    path('api/buscar-libro/<int:libro_id>/', buscar_libro),
    path('api/crear-venta/', crear_venta),
]
