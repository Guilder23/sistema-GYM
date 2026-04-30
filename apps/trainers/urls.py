from django.urls import path
from . import views

app_name = 'trainers'

urlpatterns = [
    path('', views.trainer_list, name='list'),
    path('nuevo/', views.trainer_create, name='create'),
    path('editar/<int:trainer_id>/', views.trainer_edit, name='edit'),
]
