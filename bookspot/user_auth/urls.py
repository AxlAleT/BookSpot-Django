from .api.views import *
from django.urls import path


urlpatterns = [
    path('api/login/', loginAPIView.as_view(), name='login'),
    path('api/logout/', logoutAPIView.as_view(), name='logout'),
    path('login.html', loginRenderView, name='login'),
]