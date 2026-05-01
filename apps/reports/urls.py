from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('exportar/clientes/', views.export_clients_excel, name='export_clients_excel'),
    path('exportar/accesos/', views.export_access_csv, name='export_access_csv'),
    path('exportar/pagos/', views.export_payments_pdf, name='export_payments_pdf'),
]
