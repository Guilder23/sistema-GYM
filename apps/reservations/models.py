from django.db import models
from django.utils import timezone
from apps.trainers.models import Trainer
from apps.clients.models import Client

class ClassType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")

    def __str__(self):
        return self.name

class ClassSchedule(models.Model):
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=12)
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.class_type.name} - {self.date} {self.start_time}'

    @property
    def available_spots(self):
        return self.capacity - self.reservations.filter(confirmed=True).count()

class Reservation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reservations')
    schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE, related_name='reservations')
    reserved_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.client} - {self.schedule}'
