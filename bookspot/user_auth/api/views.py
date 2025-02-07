from django.contrib.auth import login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from django.middleware.csrf import get_token
from .serializers import LoginSerializer

class loginAPIView(APIView):
    def get(self, request):
        # Return CSRF token for GET requests
        return Response({'csrfToken': get_token(request)})

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

class logoutAPIView(APIView):
    def post(self, request):
        logout(request)
        return Response({"mensaje": "Sesión cerrada exitosamente"})
