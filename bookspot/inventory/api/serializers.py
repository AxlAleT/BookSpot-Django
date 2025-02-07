from rest_framework import serializers
from core.models import Libro


class LibroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libro
        fields = ['id', 'titulo', 'precio', 'cantidad_disponible']

    def validate_cantidad_disponible(self, value):
        if value < 0:
            raise serializers.ValidationError("La cantidad disponible no puede ser negativa.")
        return value