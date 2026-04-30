from django.urls import path
from . import views

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('nuevo/', views.client_create, name='client_create'),
    path('editar/<int:client_id>/', views.client_edit, name='client_edit'),
    path('detalle/<int:client_id>/', views.client_detail, name='client_detail'),
    path('eliminar/<int:client_id>/', views.client_delete, name='client_delete'),
]
