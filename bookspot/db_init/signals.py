from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from core.models import Libro, TipoMovimiento, Grupo, Usuario

INITIAL_DATA = {
    'TIPOS_MOVIMIENTO': [
                {'nombre': 'VPV', 'descripcion': 'Venta en Punto de Venta, relacionado a la venta de un producto en la tienda fisica'},
                {'nombre': 'APV', 'descripcion': 'Apartado en Punto de Venta, relacionado a un apartado de productos en el punto de venta'},
                {'nombre': 'RLI', 'descripcion': 'Registro de libro en inventario, registra la entrada de un libro en el inventario'},
                {'nombre': 'ELI', 'descripcion': 'Eliminacion de libro en inventario, registra la eliminacion de un libro por un almacenista'},
                {'nombre': 'ELA', 'descripcion': 'Eliminacion de un apartado, cancelacion'},
                {'nombre': 'ACV', 'descripcion': 'Apartado Concretado, ahora es una Venta'},
    ],
    'GRUPOS': [
                {'nombre': 'Admin', 'descripcion': 'Grupo de administradores, con todos los permisos'},
                {'nombre': 'Vendedor', 'descripcion': 'Grupo de vendedores, con permisos limitados'},
                {'nombre': 'Almacenista', 'descripcion': 'Grupo de almacenistas, tienen permisos para hacer operaciones en el inventario'},
    ],
    'USUARIOS': [
                {
                    'nombre': 'admin nombre',
                    'telefono': '555-0100',
                    'direccion': 'Calle Admin, 123',
                    'correo_electronico': 'admin@bookspot.com',
                    'grupo': 'Admin',
                    'password': 'admin'
                },
                {
                    'nombre': 'vendedor nombre',
                    'telefono': '555-0200',
                    'direccion': 'Calle Vendedor, 456',
                    'correo_electronico': 'vendedor@bookspot.com',
                    'grupo': 'Vendedor',
                    'password': 'vendedor'
                },
                {
                    'nombre': 'almacenista nombre',
                    'telefono': '555-0300',
                    'direccion': 'Calle Almacenista, 789',
                    'correo_electronico': 'almacenista@bookspot.com',
                    'grupo': 'Almacenista',
                    'password': 'almacenista'
                }
    ],
    'LIBROS': [
         {"titulo": "El señor de los anillos", "precio": 15.99, "cantidad_disponible": 300},
         {"titulo": "Cien años de soledad", "precio": 12.99, "cantidad_disponible": 800},
         {"titulo": "Don Quijote de la Mancha", "precio": 14.99, "cantidad_disponible": 500},
         {"titulo": "Matar a un ruiseñor", "precio": 9.99, "cantidad_disponible": 1200},
         {"titulo": "1984", "precio": 8.99, "cantidad_disponible": 700},
         {"titulo": "Harry Potter y la piedra filosofal", "precio": 11.99, "cantidad_disponible": 1500},
         {"titulo": "Orgullo y prejuicio", "precio": 7.99, "cantidad_disponible": 600},
         {"titulo": "El gran Gatsby", "precio": 10.99, "cantidad_disponible": 900},
         {"titulo": "En busca del tiempo perdido", "precio": 13.99, "cantidad_disponible": 400},
         {"titulo": "Ulises", "precio": 16.99, "cantidad_disponible": 300},
     ]
}

@receiver(post_migrate)
def populate_initial_data(sender, **kwargs):
    if sender.name == 'core':
        if not Libro.objects.exists():
            _create_books()
            _create_tipos_movimiento()
            _create_grupos()
            _create_usuarios()

def _create_books():
    for book_data in INITIAL_DATA['LIBROS']:
        Libro.objects.get_or_create(**book_data)

def _create_tipos_movimiento():
    for tipo_data in INITIAL_DATA['TIPOS_MOVIMIENTO']:
        TipoMovimiento.objects.get_or_create(**tipo_data)

def _create_grupos():
    for grupo_data in INITIAL_DATA['GRUPOS']:
        Grupo.objects.get_or_create(**grupo_data)

def _create_usuarios():
    for usuario_data in INITIAL_DATA['USUARIOS']:
        grupo = Grupo.objects.get(nombre=usuario_data['grupo'])
        Usuario.objects.get_or_create(
            correo_electronico=usuario_data['correo_electronico'],
            defaults={
                'nombre': usuario_data['nombre'],
                'telefono': usuario_data['telefono'],
                'direccion': usuario_data['direccion'],
                'grupo': grupo,
                'password': make_password(usuario_data['password'])
            }
        )