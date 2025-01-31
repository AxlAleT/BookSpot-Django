from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, CheckConstraint
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator


class MetodoPago(models.Model):
    """Payment method model"""

    nombre = models.CharField(
        _('Nombre del método de pago'),
        max_length=100,  # Adjusted length for flexibility
        unique=True,
        null=False
    )
    descripcion = models.TextField(
        _('Descripción'),
        blank=True,  # Optional field
        null=True
    )

    history = HistoricalRecords()  # Enable historical tracking

    class Meta:
        verbose_name = _('Método de pago')
        verbose_name_plural = _('Métodos de pago')
        ordering = ['nombre']  # Default ordering by name

    def __str__(self):
        return self.nombre  # String representation of the model

    def to_dict(self):
        """Convert the object to a dictionary for easy serialization"""
        return {
            'id_metodo_pago': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }

class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""

    def create_user(self, correo_electronico, password=None, **extra_fields):
        if not correo_electronico:
            raise ValueError(_('El correo electrónico es obligatorio'))
        user = self.model(
            correo_electronico=self.normalize_email(correo_electronico),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo_electronico, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(correo_electronico, password, **extra_fields)


class Usuario(AbstractUser, PermissionsMixin):
    """Custom user model extending Django's AbstractUser"""

    username = None  # Disable username field
    email = None  # We're using correo_electronico instead

    nombre = models.CharField(_('Nombre completo'), max_length=100)
    telefono = models.CharField(_('Teléfono'), max_length=20, db_index=True)
    direccion = models.TextField(_('Dirección'))
    correo_electronico = models.EmailField(
        _('Correo electrónico'),
        unique=True,
        db_index=True
    )
    grupo = models.ForeignKey(
        'Grupo',
        on_delete=models.PROTECT,
        related_name='usuarios',
        verbose_name=_('Grupo de usuario'),
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'correo_electronico'
    REQUIRED_FIELDS = ['nombre', 'telefono']

    objects = CustomUserManager()

    history = HistoricalRecords(
        excluded_fields=['password', 'last_login', 'is_superuser'],
        inherit=True
    )

    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        ordering = ['nombre']
        permissions = [
            ('view_report', _('Puede ver reportes')),
            ('manage_inventory', _('Puede gestionar inventario')),
        ]

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.telefono and not self.telefono.isdigit():
            raise ValidationError({'telefono': 'El teléfono solo debe contener números'})

class Grupo(models.Model):
    """User group classification model"""

    nombre = models.CharField(_('Nombre del grupo'), max_length=50, unique=True)
    descripcion = models.TextField(_('Descripción'), blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Grupo')
        verbose_name_plural = _('Grupos')
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['nombre'],
                name='unique_grupo_nombre'
            )
        ]

    def __str__(self):
        return self.nombre

    def clean(self):
        if len(self.nombre) < 3:
            raise ValidationError({'nombre': _('El nombre del grupo debe tener al menos 3 caracteres')})


class Libro(models.Model):
    """Book inventory model"""

    titulo = models.CharField(_('Título'), max_length=100, unique=True, db_index=True)
    precio = models.DecimalField(
        _('Precio'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    cantidad_disponible = models.PositiveIntegerField(
        _('Cantidad disponible'),
        default=0
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Libro')
        verbose_name_plural = _('Libros')
        ordering = ['titulo']
        constraints = [
            CheckConstraint(
                check=Q(cantidad_disponible__gte=0),
                name='cantidad_no_negativa'
            )
        ]

    def __str__(self):
        return self.titulo

    def clean(self):
        if self.cantidad_disponible < 0:
            raise ValidationError(_('La cantidad disponible no puede ser negativa'))


class Apartado(models.Model):
    """Reservation system model"""

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='apartados',
        verbose_name=_('Usuario')
    )
    fecha_limite = models.DateTimeField(
        _('Fecha límite'),
        db_index=True
    )
    monto = models.DecimalField(
        _('Monto total'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    nombre_acreedor = models.CharField(
        _('Nombre del acreedor'),
        max_length=100
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Apartado')
        verbose_name_plural = _('Apartados')
        ordering = ['-fecha_limite']
        indexes = [
            models.Index(fields=['fecha_limite', 'usuario']),
        ]

    def __str__(self):
        return f"Apartado #{self.id} - {self.usuario.nombre}"

    def clean(self):
        if self.fecha_limite < timezone.now():
            raise ValidationError({'fecha_limite': _('La fecha límite no puede ser en el pasado')})


class DetallesApartado(models.Model):
    """Reservation details model"""

    apartado = models.ForeignKey(
        Apartado,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name=_('Apartado')
    )
    libro = models.ForeignKey(
        Libro,
        on_delete=models.PROTECT,
        verbose_name=_('Libro')
    )
    cantidad = models.PositiveIntegerField(_('Cantidad'))
    precio_apartado = models.DecimalField(
        _('Precio de apartado'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Detalle de apartado')
        verbose_name_plural = _('Detalles de apartados')
        constraints = [
            CheckConstraint(
                check=Q(cantidad__gt=0),
                name='cantidad_apartado_positiva'
            )
        ]

    def __str__(self):
        return f"Detalle #{self.id} - {self.libro.titulo}"

    def clean(self):
        if self.cantidad > self.libro.cantidad_disponible:
            raise ValidationError({
                'cantidad': _('La cantidad solicitada excede el inventario disponible')
            })


# ... (Other models following similar patterns with historical records and constraints)

class Venta(models.Model):
    """Sales transaction model"""

    fecha = models.DateTimeField(
        _('Fecha de venta'),
        auto_now_add=True,
        db_index=True
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name=_('Usuario')
    )
    monto_total = models.DecimalField(
        _('Monto total'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    metodo_pago = models.ForeignKey(
        'MetodoPago',
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name=_('Método de pago')
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Venta')
        verbose_name_plural = _('Ventas')
        ordering = ['-fecha']
        permissions = [
            ('cancel_venta', _('Puede cancelar ventas')),
        ]

    def __str__(self):
        return f"Venta #{self.id} - {self.usuario.nombre}"

    def clean(self):
        if self.monto_total <= 0:
            raise ValidationError({'monto_total': _('El monto total debe ser positivo')})


# Example of DRF Serializer (should be in serializers.py)
from rest_framework import serializers


class LibroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libro
        fields = '__all__'
        read_only_fields = ('cantidad_disponible',)

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a cero")
        return value