from django.db import models
from django.utils import timezone
from apps.clients.models import Client

class MembershipPlan(models.Model):
    name = models.CharField(max_length=120)
    duration_days = models.PositiveIntegerField(default=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Membership(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.client} - {self.plan.name}'

    @property
    def status(self):
        if self.end_date < timezone.now().date():
            return 'Vencida'
        return 'Activa'

class Payment(models.Model):
    METHODS = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments')
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, blank=True, null=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    method = models.CharField(max_length=60, choices=METHODS, default='EFECTIVO')
    receipt_code = models.CharField(max_length=70, blank=True, unique=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'Pago {self.amount} - {self.client} ({self.date:%Y-%m-%d})'

class Promotion(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    discount_percentage = models.PositiveIntegerField(default=0, help_text="Porcentaje de descuento (0-100)")
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    applicable_plans = models.ManyToManyField(MembershipPlan, related_name='promotions', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_current(self):
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date
