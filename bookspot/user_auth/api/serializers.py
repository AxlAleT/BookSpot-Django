from rest_framework import serializers
from django.contrib.auth import authenticate
from core.models import Usuario

class LoginSerializer(serializers.Serializer):
    correo_electronico = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        correo = data.get("correo_electronico")
        password = data.get("password")

        user = authenticate(request=self.context.get('request'), correo_electronico=correo, password=password)

        if not user:
            raise serializers.ValidationError("Credenciales inválidas")

        return user  # Return the user instance instead of a dictionary
