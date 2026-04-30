from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AccessRecord
from apps.clients.models import Client
from apps.memberships.models import Membership
from django.utils import timezone


@login_required
def access_panel(request):
    recent_access = AccessRecord.objects.all().order_by('-timestamp')[:20]
    
    if request.method == 'POST':
        ci = request.POST.get('ci', '').strip()
        if not ci:
            messages.error(request, 'Debes ingresar un número de CI/DNI.')
            return redirect('access_panel')
            
        try:
            client = Client.objects.get(ci=ci)
            
            # Verificar si tiene membresía activa
            active_membership = client.memberships.filter(
                active=True,
                end_date__gte=timezone.now().date()
            ).first()
            
            valid = True
            message = "Acceso concedido"
            
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

    context = {'recent_access': recent_access}
    return render(request, 'access/access_panel.html', context)


@login_required
def access_history(request):
    access_records = AccessRecord.objects.all().order_by('-timestamp')
    context = {'access_records': access_records}
    return render(request, 'access/access_history.html', context)
