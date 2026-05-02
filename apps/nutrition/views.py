from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.core.permissions import role_required, get_linked_client
from apps.core.models import UserProfile
from .models import NutritionLog
from django import forms

class NutritionLogForm(forms.ModelForm):
    class Meta:
        model = NutritionLog
        fields = ['meal_type', 'food_name', 'amount_g', 'calories', 'protein', 'carbs', 'fat']
        widgets = {
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
            'food_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pechuga de pollo'}),
            'amount_g': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Gramos'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'kcal'}),
            'protein': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'g'}),
            'carbs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'g'}),
            'fat': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'g'}),
        }

@role_required(UserProfile.ROLE_CLIENT, UserProfile.ROLE_ADMIN)
def nutrition_dashboard(request):
    client = get_linked_client(request.user)
    if not client:
        messages.error(request, "Perfil de cliente no vinculado.")
        return redirect('dashboard')
    
    logs = NutritionLog.objects.filter(client=client).order_by('-date', '-id')
    
    from django.utils import timezone
    today = timezone.now().date()
    today_logs = logs.filter(date=today)
    
    total_calories = sum(log.calories for log in today_logs)
    total_protein = sum(log.protein for log in today_logs)
    total_carbs = sum(log.carbs for log in today_logs)
    total_fat = sum(log.fat for log in today_logs)

    context = {
        'logs': logs,
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fat': total_fat,
    }
    return render(request, 'nutrition/dashboard.html', context)

@role_required(UserProfile.ROLE_CLIENT)
def log_create(request):
    client = get_linked_client(request.user)
    if request.method == 'POST':
        form = NutritionLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.client = client
            log.save()
            messages.success(request, "Registro nutricional creado.")
            return redirect('nutrition_dashboard')
    else:
        form = NutritionLogForm()
    
    return render(request, 'nutrition/log_form.html', {'form': form, 'title': 'Nuevo Registro'})

@role_required(UserProfile.ROLE_CLIENT)
def log_edit(request, log_id):
    client = get_linked_client(request.user)
    log = get_object_or_404(NutritionLog, id=log_id, client=client)
    
    if request.method == 'POST':
        form = NutritionLogForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro actualizado.")
            return redirect('nutrition_dashboard')
    else:
        form = NutritionLogForm(instance=log)
    
    return render(request, 'nutrition/log_form.html', {'form': form, 'title': 'Editar Registro'})

@role_required(UserProfile.ROLE_CLIENT)
def log_delete(request, log_id):
    client = get_linked_client(request.user)
    log = get_object_or_404(NutritionLog, id=log_id, client=client)
    
    if request.method == 'POST':
        log.delete()
        messages.success(request, "Registro eliminado.")
        return redirect('nutrition_dashboard')
    
    return render(request, 'nutrition/log_confirm_delete.html', {'log': log})
