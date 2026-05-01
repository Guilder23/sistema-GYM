from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ClassSchedule, Reservation, ClassType
from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.core.models import UserProfile
from apps.core.permissions import get_linked_trainer, get_user_role, role_required


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION, UserProfile.ROLE_TRAINER)
def reservation_list(request):
    classes = ClassSchedule.objects.all().order_by('date', 'start_time')
    if get_user_role(request.user) == UserProfile.ROLE_TRAINER:
        classes = classes.filter(trainer=get_linked_trainer(request.user))
    context = {'classes': classes}
    return render(request, 'reservations/reservation_list.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
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


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def class_edit(request, class_id):
    class_schedule = get_object_or_404(ClassSchedule, id=class_id)
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

        occupied = class_schedule.reservations.filter(confirmed=True).count()
        try:
            capacity_value = int(capacity)
        except (TypeError, ValueError):
            capacity_value = class_schedule.capacity

        if capacity_value < occupied:
            messages.error(request, f'La capacidad no puede ser menor que las reservas confirmadas ({occupied}).')
            return redirect('class_edit', class_id=class_schedule.id)

        class_schedule.class_type = class_type
        class_schedule.date = date
        class_schedule.start_time = start_time
        class_schedule.end_time = end_time
        class_schedule.capacity = capacity_value
        class_schedule.trainer = trainer
        class_schedule.save()

        messages.success(request, 'Clase actualizada correctamente.')
        return redirect('reservation_list')

    context = {
        'class_types': class_types,
        'trainers': trainers,
        'class_schedule': class_schedule,
        'editing': True,
    }
    return render(request, 'reservations/class_form.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION, UserProfile.ROLE_TRAINER)
def class_detail(request, class_id):
    classes = ClassSchedule.objects.all()
    if get_user_role(request.user) == UserProfile.ROLE_TRAINER:
        classes = classes.filter(trainer=get_linked_trainer(request.user))
    class_schedule = get_object_or_404(classes, id=class_id)

    if request.method == 'POST':
        if request.POST.get('action') == 'cancel_reservation':
            reservation_id = request.POST.get('reservation_id')
            if reservation_id:
                try:
                    reservation = Reservation.objects.get(id=reservation_id, schedule=class_schedule)
                    if not reservation.confirmed:
                        messages.warning(request, 'La reserva ya estaba cancelada.')
                    else:
                        reservation.confirmed = False
                        reservation.save(update_fields=['confirmed'])
                        messages.success(request, f'Reserva de {reservation.client.full_name} cancelada correctamente.')
                except Reservation.DoesNotExist:
                    messages.error(request, 'No se encontró la reserva especificada.')
            else:
                messages.error(request, 'Falta el identificador de la reserva.')
            return redirect('class_detail', class_id=class_schedule.id)

        ci = request.POST.get('ci', '').strip()
        if not ci:
            messages.error(request, 'Debes ingresar el CI/DNI del cliente.')
            return redirect('class_detail', class_id=class_schedule.id)

        try:
            client = Client.objects.get(ci=ci)
        except Client.DoesNotExist:
            messages.error(request, f'No se encontró ningún cliente con CI/DNI: {ci}')
            return redirect('class_detail', class_id=class_schedule.id)

        if class_schedule.available_spots <= 0:
            messages.error(request, 'No hay cupos disponibles para esta clase.')
            return redirect('class_detail', class_id=class_schedule.id)

        if Reservation.objects.filter(client=client, schedule=class_schedule, confirmed=True).exists():
            messages.warning(request, 'El cliente ya está inscrito en esta clase.')
            return redirect('class_detail', class_id=class_schedule.id)

        Reservation.objects.create(client=client, schedule=class_schedule)
        messages.success(request, f'Cliente {client.full_name} inscrito correctamente.')
        return redirect('class_detail', class_id=class_schedule.id)

    reservations = class_schedule.reservations.all()
    context = {'class': class_schedule, 'reservations': reservations}
    return render(request, 'reservations/class_detail.html', context)
