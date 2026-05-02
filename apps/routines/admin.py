from django.contrib import admin
from .models import ExerciseCategory, Exercise, Routine, RoutineExercise, RoutineProgress

@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'wger_id')
    search_fields = ('name',)

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'wger_id')
    search_fields = ('name',)
    list_filter = ('category',)

class RoutineExerciseInline(admin.TabularInline):
    model = RoutineExercise
    extra = 1

@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'trainer', 'created_at', 'active')
    search_fields = ('name', 'client__first_name', 'client__last_name')
    list_filter = ('active', 'created_at')
    inlines = [RoutineExerciseInline]

@admin.register(RoutineProgress)
class RoutineProgressAdmin(admin.ModelAdmin):
    list_display = ('client', 'routine', 'date', 'weight_kg')
    list_filter = ('date',)
