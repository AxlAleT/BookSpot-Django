from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from .serializers import LoginSerializer
from django.shortcuts import render


class loginAPIView(APIView):
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


def loginRenderView(request):
    return render(request, 'login/login.html')