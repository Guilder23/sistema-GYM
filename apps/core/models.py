from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.clients.models import Client
from apps.trainers.models import Trainer


class SystemSetting(models.Model):
    key = models.CharField(max_length=80, unique=True)
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.key


class UserProfile(models.Model):
    ROLE_ADMIN = 'ADMIN'
    ROLE_RECEPTION = 'RECEPCIONISTA'
    ROLE_TRAINER = 'ENTRENADOR'
    ROLE_CLIENT = 'CLIENTE'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrador'),
        (ROLE_RECEPTION, 'Recepcionista'),
        (ROLE_TRAINER, 'Entrenador'),
        (ROLE_CLIENT, 'Cliente'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_RECEPTION)
    profile_photo = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    client = models.OneToOneField(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_profile')
    trainer = models.OneToOneField(Trainer, on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_profile')

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'

    @property
    def role_label(self):
        return self.get_role_display()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_user_profile(sender, instance, created, **kwargs):
    default_role = UserProfile.ROLE_ADMIN if instance.is_superuser else UserProfile.ROLE_RECEPTION
    if created:
        UserProfile.objects.create(user=instance, role=default_role)
        return

    profile, created_profile = UserProfile.objects.get_or_create(
        user=instance,
        defaults={'role': default_role},
    )
    if instance.is_superuser and profile.role != UserProfile.ROLE_ADMIN:
        profile.role = UserProfile.ROLE_ADMIN
        profile.save(update_fields=['role'])
