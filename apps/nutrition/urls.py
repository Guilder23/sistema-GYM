from django.urls import path
from . import views

urlpatterns = [
    path('', views.nutrition_dashboard, name='nutrition_dashboard'),
    path('crear/', views.log_create, name='log_create'),
    path('editar/<int:log_id>/', views.log_edit, name='log_edit'),
    path('eliminar/<int:log_id>/', views.log_delete, name='log_delete'),
]
