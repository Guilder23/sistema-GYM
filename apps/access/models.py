from django.db import models
from django.utils import timezone
from apps.clients.models import Client


class AccessRecord(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    entry_type = models.CharField(max_length=50, choices=[
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ], default='ENTRADA')
    method = models.CharField(max_length=50, choices=[
        ('QR', 'QR'),
        ('CODIGO', 'Código'),
        ('HUELLA', 'Huella'),
    ], default='CODIGO')
    valid = models.BooleanField(default=True)
    message = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.client} - {self.entry_type} - {self.timestamp:%Y-%m-%d %H:%M}'
