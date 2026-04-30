from django.urls import path
from . import views

urlpatterns = [
    path('', views.routine_list, name='routine_list'),
    path('nuevo/', views.routine_create, name='routine_create'),
    path('detalle/<int:routine_id>/', views.routine_detail, name='routine_detail'),
]
