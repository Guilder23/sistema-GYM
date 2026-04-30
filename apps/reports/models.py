from django.db import models


class Report(models.Model):
    name = models.CharField(max_length=140)
    report_type = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
