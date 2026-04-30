from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.clients.models import Client

class Notification(models.Model):
    TYPES = [
        ('PAGO_VENCIDO', 'Pago vencido'),
        ('MEMBRESIA_VENCIDA', 'Membresía vencida'),
        ('CLASE_RECORDATORIO', 'Recordatorio de clase'),
        ('PROMOCION', 'Promoción'),
        ('SISTEMA', 'Sistema'),
        ('COMUNICADO', 'Comunicado General'),
    ]
    title = models.CharField(max_length=160)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=TYPES)
    
    # Recipient can be a specific Client or a Django User (for staff)
    recipient_client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    recipient_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    # If both are null, it's a global announcement
    is_global = models.BooleanField(default=False)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    sent = models.BooleanField(default=True) # Set to true by default for simple creation

    def __str__(self):
        return self.title
