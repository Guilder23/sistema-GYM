from django.db import models
from apps.clients.models import Client

class NutritionLog(models.Model):
    MEAL_CHOICES = [
        ('BREAKFAST', 'Desayuno'),
        ('LUNCH', 'Almuerzo'),
        ('DINNER', 'Cena'),
        ('SNACK', 'Snack/Otros'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='nutrition_logs')
    date = models.DateField(auto_now_add=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES, verbose_name="Tipo de Comida")
    food_name = models.CharField(max_length=200, verbose_name="Alimento")
    amount_g = models.DecimalField(max_digits=7, decimal_places=2, help_text="Cantidad en gramos", verbose_name="Cantidad (g)")
    calories = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Calorías (kcal)")
    protein = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Proteína (g)")
    carbs = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Carbohidratos (g)")
    fat = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Grasas (g)")
    
    def __str__(self):
        return f'{self.client} - {self.date} - {self.meal_type} - {self.food_name}'
