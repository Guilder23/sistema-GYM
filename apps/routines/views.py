from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.clients.models import Client
from apps.trainers.models import Trainer
from .models import Routine, Exercise, RoutineExercise


@login_required
def routine_list(request):
    search_query = request.GET.get('q', '')
    routines = Routine.objects.all().order_by('-created_at')
    if search_query:
        routines = routines.filter(
            models.Q(name__icontains=search_query) |
            models.Q(client__first_name__icontains=search_query) |
            models.Q(client__last_name__icontains=search_query)
        )
    context = {'routines': routines, 'search_query': search_query}
    return render(request, 'routines/routine_list.html', context)


@login_required
def routine_create(request):
    clients = Client.objects.filter(is_active=True).order_by('first_name', 'last_name')
    trainers = Trainer.objects.filter(active=True).order_by('full_name')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        client_id = request.POST.get('client_id')
        trainer_id = request.POST.get('trainer_id')
        notes = request.POST.get('notes', '').strip()
        
        client = get_object_or_404(Client, id=client_id)
        trainer = None
        if trainer_id:
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


@login_required
def routine_detail(request, routine_id):
    routine = get_object_or_404(Routine, id=routine_id)
    routine_exercises = routine.routine_exercises.select_related('exercise', 'exercise__category').all()
    exercises = Exercise.objects.all().order_by('category__name', 'name')
    
    if request.method == 'POST':
        exercise_id = request.POST.get('exercise_id')
        sets = request.POST.get('sets', 3)
        reps = request.POST.get('reps', '')
        rest_time = request.POST.get('rest_time', '')
        
        exercise = get_object_or_404(Exercise, id=exercise_id)
        RoutineExercise.objects.create(
            routine=routine,
            exercise=exercise,
            sets=sets,
            reps=reps,
            rest_time=rest_time
        )
        messages.success(request, 'Ejercicio añadido a la rutina.')
        return redirect('routine_detail', routine_id=routine.id)

    context = {
        'routine': routine,
        'routine_exercises': routine_exercises,
        'exercises': exercises,
    }
    return render(request, 'routines/routine_detail.html', context)
