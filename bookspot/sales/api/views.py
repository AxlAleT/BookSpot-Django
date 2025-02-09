# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from core.models import Libro, Movimiento, DetallesMovimiento, TipoMovimiento
from django.core.exceptions import ObjectDoesNotExist, ValidationError


@api_view(['GET'])
def buscar_libro(request, libro_id):
    try:
        libro = Libro.objects.get(pk=libro_id)
        return Response({
            'id': libro.id,
            'titulo': libro.titulo,
            'precio': float(libro.precio),
            'stock': libro.cantidad_disponible
        })
    except Libro.DoesNotExist:
        return Response({'error': 'Libro no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@transaction.atomic
def crear_venta(request):
    try:
        # Get authenticated user
        usuario = request.user

        # Validate required fields
        metodo_pago = request.data.get('metodo_pago')
        if metodo_pago not in dict(Movimiento.METODO_PAGO_CHOICES).keys():
            raise ValidationError('Método de pago inválido')

        items = request.data.get('items', [])
        if not items:
            raise ValidationError('Debe incluir al menos un producto')

        # Create movimiento for the sale
        tipo_movimiento = TipoMovimiento.objects.get(nombre='VPV')
        movimiento = Movimiento.objects.create(
            tipo_movimiento=tipo_movimiento,
            usuario=usuario,
            metodo_pago=metodo_pago,
            fecha_hora=timezone.now()  # Explicitly set current time
        )

        total = 0
        for item in items:
            try:
                libro = Libro.objects.get(pk=item['libro_id'])
                cantidad = int(item['cantidad'])

                # Validate stock
                if cantidad > libro.cantidad_disponible:
                    raise ValidationError(f'Stock insuficiente para {libro.titulo}')

                # Create movimiento detail
                DetallesMovimiento.objects.create(
                    movimiento=movimiento,
                    libro=libro,
                    cantidad=cantidad
                )

                # Update stock
                libro.cantidad_disponible -= cantidad
                libro.save()

                # Calculate total
                total += float(libro.precio) * cantidad

            except ObjectDoesNotExist:
                raise ValidationError(f'Libro con ID {item["libro_id"]} no encontrado')
            except ValueError:
                raise ValidationError('Cantidad debe ser un número válido')

        # Update movimiento with total amount
        movimiento.monto_total = total
        movimiento.save()

        return Response({
            'success': True,
            'movimiento_id': movimiento.id,
            'total': total,
            'fecha': movimiento.fecha_hora.isoformat(),
            'metodo_pago': movimiento.get_metodo_pago_display(),
            'usuario': {
                'id': usuario.id,
                'nombre': usuario.nombre
            }
        }, status=status.HTTP_201_CREATED)

    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

"""
@api_view(['GET'])
def obtener_ventas(request):
    try:
        # Get all sales (VPV type movements)
        ventas = Movimiento.objects.filter(
            tipo_movimiento__nombre='VPV'
        ).select_related('usuario').prefetch_related('detalles__libro')

        results = []
        for venta in ventas:
            detalles = [{
                'libro': detalle.libro.titulo,
                'cantidad': detalle.cantidad,
                'precio_unitario': float(detalle.libro.precio)
            } for detalle in venta.detalles.all()]

            results.append({
                'id': venta.id,
                'fecha': venta.fecha_hora.isoformat(),
                'total': float(venta.monto_total),
                'metodo_pago': venta.get_metodo_pago_display(),
                'usuario': {
                    'id': venta.usuario.id,
                    'nombre': venta.usuario.nombre
                },
                'detalles': detalles
            })

        return Response(results)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

"""