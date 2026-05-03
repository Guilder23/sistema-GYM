from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import AccessRecord
from apps.clients.models import Client
from apps.memberships.models import Membership
from django.utils import timezone
from apps.core.models import UserProfile
from apps.core.permissions import role_required, get_linked_client, get_user_role


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def access_panel(request):
    today = timezone.localdate()
    recent_access = AccessRecord.objects.filter(timestamp__date=today).order_by('-timestamp')
    
    entries_count = recent_access.filter(valid=True).count()
    denied_count = recent_access.filter(valid=False).count()
    qr_count = recent_access.filter(method='QR', valid=True).count()
    manual_count = recent_access.filter(method='CODIGO', valid=True).count()
    
    # URL para el QR (puedes cambiar el gym_id = 1 por algo dinámico si fuera necesario)
    gym_id = 1
    # Construir la URL absoluta para el QR usando reverse para evitar errores de prefijo
    checkin_url = request.build_absolute_uri(reverse('qr_checkin', kwargs={'gym_id': gym_id}))
    
    if request.method == 'POST':
        ci = request.POST.get('ci', '').strip()
        if not ci:
            messages.error(request, 'Debes ingresar un número de CI/DNI.')
            return redirect('access_panel')
            
        try:
            client = Client.objects.get(ci=ci)
            
            # Verificar si ya registró asistencia hoy
            already_checked_in = AccessRecord.objects.filter(
                client=client,
                timestamp__date=today,
                valid=True
            ).exists()
            
            if already_checked_in:
                messages.warning(request, f'El cliente {client.full_name} ya registró asistencia hoy.')
                return redirect('access_panel')

            # Verificar si tiene membresía activa
            active_membership = client.memberships.filter(
                active=True,
                end_date__gte=today
            ).first()
            
            valid = True
            message = "Asistencia registrada correctamente"
            
            if not client.is_active:
                valid = False
                message = "Cliente inactivo"
            elif not active_membership:
                valid = False
                message = "Sin membresía activa"
            
            # Registrar acceso
            AccessRecord.objects.create(
                client=client,
                valid=valid,
                message=message,
                method='CODIGO'
            )
            
            if valid:
                messages.success(request, f'Acceso concedido: {client.full_name}')
            else:
                messages.error(request, f'Acceso denegado: {client.full_name} - {message}')
                
        except Client.DoesNotExist:
            messages.error(request, f'No se encontró ningún cliente con CI/DNI: {ci}')
            
        return redirect('access_panel')

    context = {
        'recent_access': recent_access[:20],
        'entries_count': entries_count,
        'denied_count': denied_count,
        'qr_count': qr_count,
        'manual_count': manual_count,
        'checkin_url': checkin_url
    }
    return render(request, 'access/access_panel.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def access_history(request):
    access_records = AccessRecord.objects.all().order_by('-timestamp')
    context = {'access_records': access_records}
    return render(request, 'access/access_history.html', context)


@login_required
def qr_checkin(request, gym_id):
    client = get_linked_client(request.user)
    
    if not client:
        messages.error(request, 'Tu usuario no está vinculado a un perfil de cliente.')
        return redirect('dashboard')
        
    # Verificar si ya registró asistencia hoy
    today = timezone.localdate()
    already_checked_in = AccessRecord.objects.filter(
        client=client,
        timestamp__date=today,
        valid=True
    ).exists()
    
    if already_checked_in:
        context = {
            'success': False,
            'message': 'Ya registraste asistencia hoy',
            'client': client,
            'now': timezone.localtime()
        }
        return render(request, 'access/qr_result.html', context)
        
    # Verificar membresía activa
    active_membership = client.memberships.filter(
        active=True,
        end_date__gte=today
    ).first()
    
    valid = True
    message = "Asistencia registrada correctamente"
    
    if not client.is_active:
        valid = False
        message = "Tu cuenta de cliente está inactiva"
    elif not active_membership:
        valid = False
        message = "No tienes una membresía activa"
        
    # Registrar acceso
    AccessRecord.objects.create(
        client=client,
        valid=valid,
        message=message,
        method='QR'
    )
    
    context = {
        'success': valid,
        'message': message,
        'client': client,
        'now': timezone.localtime()
    }
    return render(request, 'access/qr_result.html', context)
