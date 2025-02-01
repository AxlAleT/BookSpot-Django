from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
from bookspot.core.models import Libro
from ..utils.decorators import requiere_almacenista
# Create your views here.
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