from django.urls import path
from .api.views import LibroListCreateAPIView, LibroRetrieveUpdateDestroyAPIView
from .views import *

urlpatterns = [
    path('libros/', LibroListCreateAPIView.as_view(), name='libro-list-create'),
    path('libros/<int:id>/', LibroRetrieveUpdateDestroyAPIView.as_view(), name='libro-detail'),
    path('inventory.html', inventoryRenderView)
]
