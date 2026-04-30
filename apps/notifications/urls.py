from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('comunicado/nuevo/', views.create_announcement, name='create_announcement'),
    path('<int:notification_id>/leer/', views.mark_as_read, name='mark_notification_as_read'),
]
