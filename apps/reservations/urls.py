from django.urls import path
from . import views

urlpatterns = [
    path('', views.reservation_list, name='reservation_list'),
    path('clase/nueva/', views.class_create, name='class_create'),
    path('clase/<int:class_id>/', views.class_detail, name='class_detail'),
    path('clase/<int:class_id>/editar/', views.class_edit, name='class_edit'),
]
