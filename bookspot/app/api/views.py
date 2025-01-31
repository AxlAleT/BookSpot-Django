from rest_framework.decorators import api_view
from django.http import JsonResponse
from ..models import Libro
from ..utils.decorators import requiere_almacenista
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from .serializers import LoginSerializer
from django.shortcuts import render


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)
            return Response({
                "mensaje": "Inicio de sesión exitoso",
                "usuario": {
                    "id": user.id,
                    "nombre": user.nombre,
                    "correo_electronico": user.correo_electronico,
                    "grupo": user.grupo.nombre if user.grupo else None
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"mensaje": "Sesión cerrada exitosamente"})


def login_view(request):
    return render(request, 'login/login.html')


@api_view(['GET'])
@requiere_almacenista
def obtener_libros(request):
    try:
        numero = int(request.GET.get('numero', 0))

        if numero < 0 or numero % 100 != 0:
            return JsonResponse({"error": "El número debe ser un múltiplo de 100 y no negativo."}, status=400)

        libros = Libro.objects.all()[numero:numero + 100]
        libros_data = [{
            "id": libro.id,
            "titulo": libro.titulo,
            "precio": str(libro.precio),
            "cantidad_disponible": libro.cantidad_disponible
        } for libro in libros]

        return JsonResponse(libros_data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)