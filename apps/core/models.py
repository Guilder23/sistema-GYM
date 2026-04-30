from django.db import models


class SystemSetting(models.Model):
    key = models.CharField(max_length=80, unique=True)
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.key
