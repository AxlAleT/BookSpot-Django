# backends.py
from django.contrib.auth.backends import ModelBackend
from core.models import Usuario

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, correo_electronico=None, password=None, **kwargs):
        try:
            user = Usuario.objects.get(correo_electronico=correo_electronico)
            if user.check_password(password):
                return user
        except Usuario.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None