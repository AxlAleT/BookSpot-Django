# views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.models import Libro
from .serializers import LibroSerializer
from user_auth.utils.permissions import GrupoPermission

class LibroListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint to list and create libros.
    Only accessible to users in the 'almacenista' group.
    """
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
    permission_classes = [IsAuthenticated, GrupoPermission]
    grupo_requerido = 'Almacenista'  # Specify the required group

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class LibroRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a libro.
    Only accessible to users in the 'almacenista' group.
    """
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
    permission_classes = [IsAuthenticated, GrupoPermission]
    grupo_requerido = 'Almacenista'  # Specify the required group
    lookup_field = 'id'