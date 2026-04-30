from django.db import models
from django.utils import timezone
from apps.trainers.models import Trainer

class Client(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    ci = models.CharField(max_length=40, unique=True)
    phone = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    profile_photo = models.ImageField(upload_to='clientes/', blank=True, null=True)
    join_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, blank=True, null=True, related_name='clients')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def bmi(self):
        if self.height_cm and self.weight_kg:
            meters = self.height_cm / 100
            return round(self.weight_kg / (meters * meters), 1)
        return None

class PhysicalDataHistory(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='physical_history')
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.client} - {self.date}'

class Attendance(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='attendances')
    check_in = models.DateTimeField(default=timezone.now)
    check_out = models.DateTimeField(null=True, blank=True)
    method = models.CharField(max_length=50, choices=[
        ('QR', 'QR'),
        ('CODIGO', 'Código'),
        ('HUELLA', 'Huella'),
    ], default='CODIGO')
    valid = models.BooleanField(default=True)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.client} - {self.check_in:%Y-%m-%d %H:%M}'
