from rest_framework import serializers
from django.contrib.auth import authenticate
from core.models import Usuario

class LoginSerializer(serializers.Serializer):
    correo_electronico = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(
            correo_electronico=data['correo_electronico'],
            password=data['password']
        )
        if not user:
            raise serializers.ValidationError("Correo electrónico o contraseña incorrectos")
        return user