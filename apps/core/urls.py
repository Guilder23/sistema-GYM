from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('usuarios/', views.user_list, name='user_list'),
    path('usuarios/nuevo/', views.user_create, name='user_create'),
    path('usuarios/<int:user_id>/editar/', views.user_edit, name='user_edit'),
    path('mi-perfil/', views.my_profile, name='my_profile'),
    path('mis-pagos/', views.my_payments, name='my_payments'),
    path('mis-rutinas/', views.my_routines, name='my_routines'),
    path('mis-reservas/', views.my_reservations, name='my_reservations'),
    path('configuracion/', views.system_settings, name='system_settings'),
    path('chatbot/chat/', views.chatbot_chat, name='chatbot_chat'),
]
