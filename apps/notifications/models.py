from django.db import models
from django.utils import timezone
from apps.clients.models import Client

class Notification(models.Model):
    TYPES = [
        ('PAGO_VENCIDO', 'Pago vencido'),
        ('MEMBRESIA_VENCIDA', 'Membresía vencida'),
        ('CLASE_RECORDATORIO', 'Recordatorio de clase'),
        ('PROMOCION', 'Promoción'),
        ('SISTEMA', 'Sistema'),
    ]
    title = models.CharField(max_length=160)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=TYPES)
    recipient = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return self.title
