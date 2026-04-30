from django.db import models

class Trainer(models.Model):
    full_name = models.CharField(max_length=140)
    specialty = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    profile_photo = models.ImageField(upload_to='trainers/', blank=True, null=True)
    active = models.BooleanField(default=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.full_name
