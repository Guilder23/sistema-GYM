from datetime import timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.access.models import AccessRecord
from apps.clients.models import Client
from apps.inventory.models import Product
from apps.memberships.models import Membership, Payment
from apps.notifications.models import Notification
from apps.reservations.models import ClassSchedule, Reservation
from apps.routines.models import Routine
from apps.trainers.models import Trainer

from .models import SystemSetting, UserProfile
from .permissions import (
    get_linked_client,
    get_linked_trainer,
    get_user_profile,
    get_user_role,
    role_required,
)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.POST.get('next') or 'dashboard')
        messages.error(request, 'Credenciales inválidas. Intenta de nuevo.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    role = get_user_role(request.user)
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)

    if role == UserProfile.ROLE_ADMIN:
        total_income = Payment.objects.filter(date__date__gte=month_ago).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        expiring_memberships_count = Membership.objects.filter(
            active=True,
            end_date__gte=today,
            end_date__lte=today + timedelta(days=7),
        ).count()

        context = {
            'clients_count': Client.objects.count(),
            'active_memberships_count': Membership.objects.filter(
                active=True,
                end_date__gte=today,
            ).count(),
            'last_payments': Payment.objects.order_by('-date')[:5],
            'recent_access': AccessRecord.objects.order_by('-timestamp')[:5],
            'upcoming_classes': ClassSchedule.objects.filter(date__gte=today).order_by('date', 'start_time')[:5],
            'products_low_stock': Product.objects.filter(stock__lte=models.F('min_stock')),
            'notifications': Notification.objects.filter(sent=True).order_by('-created_at')[:4],
            'active_clients': Client.objects.filter(is_active=True).count(),
            'inactive_clients': Client.objects.filter(is_active=False).count(),
            'total_income': total_income,
            'today_attendance_count': AccessRecord.objects.filter(timestamp__date=today, valid=True).count(),
            'expiring_memberships_count': expiring_memberships_count,
        }
        return render(request, 'core/dashboard.html', context)

    if role == UserProfile.ROLE_RECEPTION:
        expiring_memberships = Membership.objects.filter(
            active=True,
            end_date__gte=today,
            end_date__lte=today + timedelta(days=7),
        ).select_related('client', 'plan')
        context = {
            'recent_access': AccessRecord.objects.order_by('-timestamp')[:8],
            'last_payments': Payment.objects.order_by('-date')[:8],
            'expiring_memberships': expiring_memberships[:8],
            'today_income': Payment.objects.filter(date__date=today).aggregate(
                total=models.Sum('amount')
            )['total'] or 0,
            'today_access_count': AccessRecord.objects.filter(timestamp__date=today, valid=True).count(),
            'pending_notifications': Notification.objects.filter(sent=True, is_read=False).count(),
        }
        return render(request, 'core/dashboard_reception.html', context)

    if role == UserProfile.ROLE_TRAINER:
        trainer = get_linked_trainer(request.user)
        if not trainer:
            messages.error(request, 'Tu cuenta de entrenador no está vinculada a un perfil.')
            return redirect('logout')
        trainer_clients = Client.objects.filter(trainer=trainer).order_by('first_name', 'last_name')
        trainer_routines = Routine.objects.filter(
            models.Q(trainer=trainer) | models.Q(client__trainer=trainer)
        ).distinct()
        trainer_classes = ClassSchedule.objects.filter(trainer=trainer, date__gte=today).order_by('date', 'start_time')
        context = {
            'trainer': trainer,
            'assigned_clients': trainer_clients[:6],
            'assigned_clients_count': trainer_clients.count(),
            'active_routines_count': trainer_routines.filter(active=True).count(),
            'upcoming_classes': trainer_classes[:6],
            'upcoming_classes_count': trainer_classes.count(),
            'recent_routines': trainer_routines.order_by('-created_at')[:6],
        }
        return render(request, 'core/dashboard_trainer.html', context)

    if role == UserProfile.ROLE_CLIENT:
        client = get_linked_client(request.user)
        if not client:
            messages.error(request, 'Tu cuenta de cliente no está vinculada a un perfil.')
            return redirect('logout')
        current_membership = client.memberships.order_by('-start_date').first()
        context = {
            'client': client,
            'current_membership': current_membership,
            'latest_payments': client.payments.order_by('-date')[:5],
            'latest_routines': client.routines.order_by('-created_at')[:5],
            'upcoming_reservations': client.reservations.select_related('schedule', 'schedule__class_type').order_by(
                'schedule__date', 'schedule__start_time'
            )[:5],
            'notifications': client.notifications.filter(sent=True).order_by('-created_at')[:5],
        }
        return render(request, 'core/dashboard_client.html', context)

    messages.error(request, 'Tu cuenta no tiene un rol asignado.')
    return redirect('logout')


@role_required(UserProfile.ROLE_ADMIN)
def system_settings(request):
    settings = SystemSetting.objects.all().order_by('key')
    if request.method == 'POST':
        for item in settings:
            value = request.POST.get(item.key, item.value)
            item.value = value
            item.save()
        messages.success(request, 'Configuración actualizada correctamente.')
        return redirect('system_settings')

    return render(request, 'core/settings.html', {'settings': settings})


@role_required(UserProfile.ROLE_ADMIN)
def user_list(request):
    users = User.objects.select_related('profile').order_by('username')
    return render(request, 'core/user_list.html', {'users': users})


def _assign_profile_relations(profile, role, client_id, trainer_id, current_user_id=None):
    profile.role = role
    profile.client = None
    profile.trainer = None

    if role == UserProfile.ROLE_CLIENT:
        if not client_id:
            raise ValueError('Debes seleccionar un cliente para este usuario.')
        conflict = UserProfile.objects.filter(client_id=client_id).exclude(user_id=current_user_id).exists()
        if conflict:
            raise ValueError('Ese cliente ya está vinculado a otro usuario.')
        profile.client = Client.objects.get(id=client_id)

    if role == UserProfile.ROLE_TRAINER:
        if not trainer_id:
            raise ValueError('Debes seleccionar un entrenador para este usuario.')
        conflict = UserProfile.objects.filter(trainer_id=trainer_id).exclude(user_id=current_user_id).exists()
        if conflict:
            raise ValueError('Ese entrenador ya está vinculado a otro usuario.')
        profile.trainer = Trainer.objects.get(id=trainer_id)


@role_required(UserProfile.ROLE_ADMIN)
def user_create(request):
    clients = Client.objects.filter(auth_profile__isnull=True).order_by('first_name', 'last_name')
    trainers = Trainer.objects.filter(auth_profile__isnull=True).order_by('full_name')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', UserProfile.ROLE_RECEPTION)

        if not username or not password:
            messages.error(request, 'Usuario y contraseña son obligatorios.')
            return render(request, 'core/user_form.html', {
                'clients': clients,
                'trainers': trainers,
                'role_choices': UserProfile.ROLE_CHOICES,
            })

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ese nombre de usuario ya existe.')
            return render(request, 'core/user_form.html', {
                'clients': clients,
                'trainers': trainers,
                'role_choices': UserProfile.ROLE_CHOICES,
            })

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=request.POST.get('first_name', '').strip(),
            last_name=request.POST.get('last_name', '').strip(),
            email=request.POST.get('email', '').strip(),
            is_staff=(role == UserProfile.ROLE_ADMIN),
            is_active=(request.POST.get('is_active') == 'on'),
        )
        profile = get_user_profile(user)
        try:
            _assign_profile_relations(
                profile,
                role,
                request.POST.get('client_id'),
                request.POST.get('trainer_id'),
                current_user_id=user.id,
            )
            profile.save()
            
            # Handle photo upload
            if request.FILES.get('profile_photo'):
                profile.profile_photo = request.FILES.get('profile_photo')
                profile.save()
        except Exception as exc:
            user.delete()
            messages.error(request, str(exc))
            return render(request, 'core/user_form.html', {
                'clients': clients,
                'trainers': trainers,
                'role_choices': UserProfile.ROLE_CHOICES,
            })

        messages.success(request, 'Usuario creado correctamente.')
        return redirect('user_list')

    return render(request, 'core/user_form.html', {
        'clients': clients,
        'trainers': trainers,
        'role_choices': UserProfile.ROLE_CHOICES,
    })


@role_required(UserProfile.ROLE_ADMIN)
def user_edit(request, user_id):
    managed_user = get_object_or_404(User, id=user_id)
    profile = get_user_profile(managed_user)
    clients = Client.objects.filter(
        models.Q(auth_profile__isnull=True) | models.Q(auth_profile=profile)
    ).order_by('first_name', 'last_name')
    trainers = Trainer.objects.filter(
        models.Q(auth_profile__isnull=True) | models.Q(auth_profile=profile)
    ).order_by('full_name')

    if request.method == 'POST':
        managed_user.username = request.POST.get('username', '').strip()
        managed_user.first_name = request.POST.get('first_name', '').strip()
        managed_user.last_name = request.POST.get('last_name', '').strip()
        managed_user.email = request.POST.get('email', '').strip()
        managed_user.is_active = request.POST.get('is_active') == 'on'

        role = request.POST.get('role', profile.role)
        managed_user.is_staff = (role == UserProfile.ROLE_ADMIN)

        password = request.POST.get('password', '').strip()
        if password:
            managed_user.set_password(password)

        try:
            _assign_profile_relations(
                profile,
                role,
                request.POST.get('client_id'),
                request.POST.get('trainer_id'),
                current_user_id=managed_user.id,
            )
            managed_user.save()
            
            if request.FILES.get('profile_photo'):
                profile.profile_photo = request.FILES.get('profile_photo')
                
            profile.save()
        except Exception as exc:
            messages.error(request, str(exc))
            return render(request, 'core/user_form.html', {
                'managed_user': managed_user,
                'profile': profile,
                'clients': clients,
                'trainers': trainers,
                'role_choices': UserProfile.ROLE_CHOICES,
            })

        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('user_list')

    return render(request, 'core/user_form.html', {
        'managed_user': managed_user,
        'profile': profile,
        'clients': clients,
        'trainers': trainers,
        'role_choices': UserProfile.ROLE_CHOICES,
    })


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION, UserProfile.ROLE_TRAINER, UserProfile.ROLE_CLIENT)
def my_profile(request):
    role = get_user_role(request.user)
    profile = get_user_profile(request.user)
    
    if request.method == 'POST':
        # Update common user info
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        
        if request.FILES.get('profile_photo'):
            profile.profile_photo = request.FILES.get('profile_photo')
            
        password = request.POST.get('password', '').strip()
        if password:
            request.user.set_password(password)
            
        request.user.save()
        profile.save()
        
        # If client, update client model too
        if role == UserProfile.ROLE_CLIENT and profile.client:
            profile.client.first_name = request.user.first_name
            profile.client.last_name = request.user.last_name
            profile.client.email = request.user.email
            if profile.profile_photo:
                profile.client.profile_photo = profile.profile_photo
            profile.client.save()
            
        messages.success(request, 'Perfil actualizado correctamente.')
        if password:
            return redirect('login') # Re-login if password changed
        return redirect('my_profile')

    if role == UserProfile.ROLE_CLIENT:
        client = get_linked_client(request.user)
        if not client:
            messages.error(request, 'No tienes un perfil de cliente vinculado.')
            return redirect('dashboard')
        memberships = client.memberships.order_by('-start_date')
        payments = client.payments.order_by('-date')
        physical_history = client.physical_history.order_by('-date')
        return render(request, 'core/client_profile.html', {
            'client': client,
            'memberships': memberships,
            'payments': payments,
            'physical_history': physical_history,
        })
    
    # For other roles (Admin, Receptionist, Trainer)
    return render(request, 'core/staff_profile.html', {
        'profile': profile,
    })


@role_required(UserProfile.ROLE_CLIENT)
def my_payments(request):
    client = get_linked_client(request.user)
    if not client:
        messages.error(request, 'No tienes un perfil de cliente vinculado.')
        return redirect('dashboard')
    return render(request, 'core/client_payments.html', {
        'client': client,
        'payments': client.payments.order_by('-date'),
    })


@role_required(UserProfile.ROLE_CLIENT)
def my_routines(request):
    client = get_linked_client(request.user)
    if not client:
        messages.error(request, 'No tienes un perfil de cliente vinculado.')
        return redirect('dashboard')
    routines = client.routines.prefetch_related('routine_exercises', 'routine_exercises__exercise').order_by('-created_at')
    return render(request, 'core/client_routines.html', {
        'client': client,
        'routines': routines,
    })


@role_required(UserProfile.ROLE_CLIENT)
def my_reservations(request):
    client = get_linked_client(request.user)
    if not client:
        messages.error(request, 'No tienes un perfil de cliente vinculado.')
        return redirect('dashboard')
    reservations = client.reservations.select_related('schedule', 'schedule__class_type', 'schedule__trainer').order_by(
        'schedule__date', 'schedule__start_time'
    )
    return render(request, 'core/client_reservations.html', {
        'client': client,
        'reservations': reservations,
    })
