from django.urls import path
from . import views

urlpatterns = [
    path('planes/', views.membership_plans, name='plan_list'),
    path('planes/nuevo/', views.membership_plan_create, name='plan_create'),
    path('pagos/', views.payment_history, name='payment_list'),
    path('pagos/registrar/', views.payment_create, name='payment_create'),
    path('asignar/<int:client_id>/', views.membership_for_client, name='membership_for_client'),
]
