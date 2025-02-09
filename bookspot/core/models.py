from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, CheckConstraint
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator


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


class TipoMovimiento(models.Model):
    """Type of inventory movement (e.g., sale, purchase, adjustment)"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Tipo de Movimiento"
        verbose_name_plural = "Tipos de Movimiento"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }


class Movimiento(models.Model):
    """Main inventory movement record"""
    METODO_PAGO_CHOICES = [
        ('TDC', 'Tarjeta de Crédito'),
        ('TDB', 'Tarjeta de Débito'),
        ('EFE', 'Efectivo'),
    ]

    tipo_movimiento = models.ForeignKey(
        TipoMovimiento,
        on_delete=models.PROTECT,
        related_name='movimientos'
    )
    usuario = models.ForeignKey(
        'Usuario',
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name=_('Usuario que realizó el movimiento')
    )
    fecha_hora = models.DateTimeField(default=timezone.now)
    monto_total = models.DecimalField(
        _('Monto total'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.01)]
    )
    metodo_pago = models.CharField(
        _('Método de pago'),
        max_length=3,
        choices=METODO_PAGO_CHOICES,
        null=True,
        blank=True
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"

    def to_dict(self):
        return {
            'id': self.id,
            'tipo_movimiento': self.tipo_movimiento.to_dict(),
            'usuario': {
                'id': self.usuario.id,
                'nombre': self.usuario.nombre
            },
            'fecha_hora': self.fecha_hora.isoformat(),
            'monto_total': float(self.monto_total) if self.monto_total else None,
            'metodo_pago': self.metodo_pago
        }


class DetallesMovimiento(models.Model):
    """Detailed items within a movement"""
    movimiento = models.ForeignKey(
        Movimiento,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    libro = models.ForeignKey(
        'Libro',
        on_delete=models.PROTECT,
        related_name='movimientos'
    )
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Detalle de Movimiento"
        verbose_name_plural = "Detalles de Movimiento"
        constraints = [
            models.UniqueConstraint(
                fields=['movimiento', 'libro'],
                name='unique_movimiento_libro'
            )
        ]

    def __str__(self):
        return f"{self.cantidad}x {self.libro} en {self.movimiento}"

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero")

    def to_dict(self):
        return {
            'id': self.id,
            'movimiento_id': self.movimiento.id,
            'libro_id': self.libro.id,
            'cantidad': self.cantidad
        }