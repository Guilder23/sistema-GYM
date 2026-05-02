from django.urls import path
from . import views

urlpatterns = [
    path('', views.routine_list, name='routine_list'),
    path('nuevo/', views.routine_create, name='routine_create'),
    path('editar/<int:routine_id>/', views.routine_edit, name='routine_edit'),
    path('detalle/<int:routine_id>/', views.routine_detail, name='routine_detail'),
    path('detalle/<int:routine_id>/progreso/', views.log_progress, name='log_progress'),
    path('detalle/<int:routine_id>/ejercicio/<int:item_id>/eliminar/', views.routine_exercise_delete, name='routine_exercise_delete'),
]
