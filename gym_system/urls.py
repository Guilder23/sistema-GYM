from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('clientes/', include('apps.clients.urls')),
    path('membresias/', include('apps.memberships.urls')),
    path('acceso/', include('apps.access.urls')),
    path('rutinas/', include('apps.routines.urls')),
    path('entrenadores/', include('apps.trainers.urls')),
    path('reservas/', include('apps.reservations.urls')),
    path('inventario/', include('apps.inventory.urls')),
    path('notificaciones/', include('apps.notifications.urls')),
    path('reportes/', include('apps.reports.urls')),
    path('nutricion/', include('apps.nutrition.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
