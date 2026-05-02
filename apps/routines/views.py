from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from apps.clients.models import Client
from apps.trainers.models import Trainer
from .models import Routine, Exercise, RoutineExercise, RoutineProgress
from apps.core.models import UserProfile
from apps.core.permissions import get_linked_trainer, get_user_role, role_required, get_linked_client


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_TRAINER, UserProfile.ROLE_CLIENT)
def log_progress(request, routine_id):
    routine = get_object_or_404(Routine, id=routine_id)
    
    # Solo el cliente dueño de la rutina o admin/entrenador pueden ver/registrar
    user_role = get_user_role(request.user)
    if user_role == UserProfile.ROLE_CLIENT:
        client = get_linked_client(request.user)
        if routine.client != client:
            messages.error(request, 'No tienes permiso para registrar progreso en esta rutina.')
            return redirect('dashboard')
    
    if request.method == 'POST':
        weight_kg = request.POST.get('weight_kg')
        notes = request.POST.get('notes', '').strip()
        
        RoutineProgress.objects.create(
            client=routine.client,
            routine=routine,
            weight_kg=weight_kg if weight_kg else None,
            notes=notes
        )
        messages.success(request, 'Progreso registrado correctamente.')
        
        if user_role == UserProfile.ROLE_CLIENT:
            return redirect('my_routines')
        return redirect('routine_detail', routine_id=routine.id)
    
    # Obtener historial de progreso
    progress_history = RoutineProgress.objects.filter(routine=routine).order_by('-date')
    
    context = {
        'routine': routine,
        'progress_history': progress_history,
    }
    return render(request, 'routines/log_progress.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_TRAINER)
def routine_list(request):
    search_query = request.GET.get('q', '')
    routines = Routine.objects.all().order_by('-created_at')
    if get_user_role(request.user) == UserProfile.ROLE_TRAINER:
        trainer = get_linked_trainer(request.user)
        routines = routines.filter(models.Q(trainer=trainer) | models.Q(client__trainer=trainer)).distinct()
    if search_query:
        routines = routines.filter(
            models.Q(name__icontains=search_query) |
            models.Q(client__first_name__icontains=search_query) |
            models.Q(client__last_name__icontains=search_query)
        )
    context = {'routines': routines, 'search_query': search_query}
    return render(request, 'routines/routine_list.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_TRAINER)
def routine_create(request):
    clients = Client.objects.filter(is_active=True).order_by('first_name', 'last_name')
    trainers = Trainer.objects.filter(active=True).order_by('full_name')
    current_role = get_user_role(request.user)
    linked_trainer = get_linked_trainer(request.user)

    if current_role == UserProfile.ROLE_TRAINER:
        # Un entrenador puede ver sus alumnos asignados Y alumnos que no tienen entrenador
        clients = clients.filter(
            models.Q(trainer=linked_trainer) | models.Q(trainer__isnull=True)
        ).distinct()
        trainers = trainers.filter(id=linked_trainer.id if linked_trainer else None)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        client_id = request.POST.get('client_id')
        trainer_id = request.POST.get('trainer_id')
        notes = request.POST.get('notes', '').strip()
        
        client = get_object_or_404(clients, id=client_id)
        trainer = None
        if current_role == UserProfile.ROLE_TRAINER:
            trainer = linked_trainer
            # Si el cliente no tiene entrenador, se le asigna automáticamente este entrenador
            if not client.trainer:
                client.trainer = linked_trainer
                client.save(update_fields=['trainer'])
        elif trainer_id:
            trainer = get_object_or_404(Trainer, id=trainer_id)
            
        routine = Routine.objects.create(
            name=name,
            client=client,
            trainer=trainer,
            notes=notes
        )
        messages.success(request, 'Rutina creada correctamente. Ahora puedes añadir ejercicios.')
        return redirect('routine_detail', routine_id=routine.id)
    
    context = {'clients': clients, 'trainers': trainers}
    return render(request, 'routines/routine_form.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_TRAINER)
def routine_edit(request, routine_id):
    clients = Client.objects.filter(is_active=True).order_by('first_name', 'last_name')
    trainers = Trainer.objects.filter(active=True).order_by('full_name')
    current_role = get_user_role(request.user)
    linked_trainer = get_linked_trainer(request.user)

    if current_role == UserProfile.ROLE_TRAINER:
        # Un entrenador puede ver sus alumnos asignados Y alumnos que no tienen entrenador
        clients = clients.filter(
            models.Q(trainer=linked_trainer) | models.Q(trainer__isnull=True)
        ).distinct()
        trainers = trainers.filter(id=linked_trainer.id if linked_trainer else None)

    routine_queryset = Routine.objects.all()
    if current_role == UserProfile.ROLE_TRAINER:
        trainer = get_linked_trainer(request.user)
        routine_queryset = routine_queryset.filter(
            models.Q(trainer=trainer) | models.Q(client__trainer=trainer)
        ).distinct()

    routine = get_object_or_404(routine_queryset, id=routine_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        client_id = request.POST.get('client_id')
        trainer_id = request.POST.get('trainer_id')
        notes = request.POST.get('notes', '').strip()

        client = get_object_or_404(clients, id=client_id)
        trainer = None
        if current_role == UserProfile.ROLE_TRAINER:
            trainer = linked_trainer
            # Si el cliente no tiene entrenador, se le asigna automáticamente este entrenador
            if not client.trainer:
                client.trainer = linked_trainer
                client.save(update_fields=['trainer'])
        elif trainer_id:
            trainer = get_object_or_404(Trainer, id=trainer_id)

        routine.name = name
        routine.client = client
        routine.trainer = trainer
        routine.notes = notes
        routine.save()

        messages.success(request, 'Rutina actualizada correctamente.')
        return redirect('routine_detail', routine_id=routine.id)

    context = {
        'clients': clients,
        'trainers': trainers,
        'routine': routine,
        'is_edit': True,
    }
    return render(request, 'routines/routine_form.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_TRAINER)
def routine_detail(request, routine_id):
    routine_queryset = Routine.objects.all()
    if get_user_role(request.user) == UserProfile.ROLE_TRAINER:
        trainer = get_linked_trainer(request.user)
        routine_queryset = routine_queryset.filter(
            models.Q(trainer=trainer) | models.Q(client__trainer=trainer)
        ).distinct()
    routine = get_object_or_404(routine_queryset, id=routine_id)
    routine_exercises = routine.routine_exercises.select_related('exercise', 'exercise__category').all()
    exercises = Exercise.objects.all().order_by('category__name', 'name')
    
    if request.method == 'POST':
        exercise_id = request.POST.get('exercise_id')
        sets = request.POST.get('sets', 3)
        reps = request.POST.get('reps', '')
        rest_time = request.POST.get('rest_time', '')
        intensity = request.POST.get('intensity', 'Media')
        weight_kg = request.POST.get('weight_kg')
        duration_minutes = request.POST.get('duration_minutes')
        
        exercise = get_object_or_404(Exercise, id=exercise_id)
        RoutineExercise.objects.create(
            routine=routine,
            exercise=exercise,
            sets=sets,
            reps=reps,
            rest_time=rest_time,
            intensity=intensity,
            weight_kg=weight_kg if weight_kg else None,
            duration_minutes=duration_minutes if duration_minutes else None
        )
        messages.success(request, 'Ejercicio añadido a la rutina.')
        return redirect('routine_detail', routine_id=routine.id)

    context = {
        'routine': routine,
        'routine_exercises': routine_exercises,
        'exercises': exercises,
    }
    return render(request, 'routines/routine_detail.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_TRAINER)
def routine_exercise_delete(request, routine_id, item_id):
    routine_queryset = Routine.objects.all()
    if get_user_role(request.user) == UserProfile.ROLE_TRAINER:
        trainer = get_linked_trainer(request.user)
        routine_queryset = routine_queryset.filter(
            models.Q(trainer=trainer) | models.Q(client__trainer=trainer)
        ).distinct()

    routine = get_object_or_404(routine_queryset, id=routine_id)
    routine_exercise = get_object_or_404(RoutineExercise, id=item_id, routine=routine)

    if request.method == 'POST':
        routine_exercise.delete()
        messages.success(request, 'Ejercicio eliminado de la rutina.')

    return redirect('routine_detail', routine_id=routine.id)
