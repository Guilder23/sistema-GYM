from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ClassSchedule, Reservation, ClassType
from apps.trainers.models import Trainer


@login_required
def reservation_list(request):
    classes = ClassSchedule.objects.all().order_by('date', 'start_time')
    context = {'classes': classes}
    return render(request, 'reservations/reservation_list.html', context)


@login_required
def class_create(request):
    class_types = ClassType.objects.all()
    trainers = Trainer.objects.filter(active=True).order_by('full_name')
    
    if request.method == 'POST':
        type_id = request.POST.get('type_id')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        capacity = request.POST.get('capacity', 12)
        trainer_id = request.POST.get('trainer_id')
        
        class_type = get_object_or_404(ClassType, id=type_id)
        trainer = None
        if trainer_id:
            trainer = get_object_or_404(Trainer, id=trainer_id)
            
        ClassSchedule.objects.create(
            class_type=class_type,
            date=date,
            start_time=start_time,
            end_time=end_time,
            capacity=capacity,
            trainer=trainer
        )
        messages.success(request, 'Clase programada correctamente.')
        return redirect('reservation_list')
        
    context = {'class_types': class_types, 'trainers': trainers}
    return render(request, 'reservations/class_form.html', context)


@login_required
def class_detail(request, class_id):
    class_schedule = get_object_or_404(ClassSchedule, id=class_id)
    reservations = class_schedule.reservations.all()
    context = {'class': class_schedule, 'reservations': reservations}
    return render(request, 'reservations/class_detail.html', context)
