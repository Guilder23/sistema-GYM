from django.db import models
from apps.clients.models import Client
from apps.trainers.models import Trainer

class ExerciseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Exercise(models.Model):
    name = models.CharField(max_length=140)
    category = models.ForeignKey(ExerciseCategory, on_delete=models.CASCADE, related_name='exercises')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='exercises/', blank=True, null=True)

    def __str__(self):
        return self.name

class Routine(models.Model):
    name = models.CharField(max_length=140)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='routines')
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_routines')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} - {self.client}'

class RoutineExercise(models.Model):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='routine_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    sets = models.PositiveIntegerField(default=3)
    reps = models.CharField(max_length=50, blank=True)
    rest_time = models.CharField(max_length=50, blank=True, help_text="e.g. 60s")
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.routine.name} - {self.exercise.name}'

class RoutineProgress(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='progress_logs')
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'Progreso {self.routine} - {self.date}'
