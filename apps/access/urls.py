from django.urls import path
from . import views

urlpatterns = [
    path('', views.access_panel, name='access_panel'),
    path('historial/', views.access_history, name='access_history'),
    path('checkin/<int:gym_id>/', views.qr_checkin, name='qr_checkin'),
]
