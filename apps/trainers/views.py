from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trainer

@login_required
def trainer_list(request):
    trainers = Trainer.objects.all().order_by('full_name')
    return render(request, 'trainers/trainer_list.html', {'trainers': trainers})

@login_required
def trainer_create(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        specialty = request.POST.get('specialty', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        bio = request.POST.get('bio', '')
        
        Trainer.objects.create(
            full_name=full_name,
            specialty=specialty,
            phone=phone,
            email=email,
            bio=bio
        )
        messages.success(request, 'Entrenador registrado correctamente.')
        return redirect('trainers:list')
    
    return render(request, 'trainers/trainer_form.html')

@login_required
def trainer_edit(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    if request.method == 'POST':
        trainer.full_name = request.POST.get('full_name')
        trainer.specialty = request.POST.get('specialty', '')
        trainer.phone = request.POST.get('phone', '')
        trainer.email = request.POST.get('email', '')
        trainer.bio = request.POST.get('bio', '')
        trainer.active = request.POST.get('active') == 'on'
        
        trainer.save()
        messages.success(request, 'Entrenador actualizado correctamente.')
        return redirect('trainers:list')
    
    return render(request, 'trainers/trainer_form.html', {'trainer': trainer})
