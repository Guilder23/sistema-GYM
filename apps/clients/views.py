from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from decimal import Decimal, InvalidOperation
from apps.clients.models import Client, PhysicalDataHistory
from apps.memberships.models import Membership, Payment
from apps.access.models import AccessRecord
from apps.core.models import UserProfile
from apps.core.permissions import get_linked_client, get_linked_trainer, get_user_role, role_required


def _get_role_scoped_clients(request):
    role = get_user_role(request.user)
    clients = Client.objects.all()
    if role == UserProfile.ROLE_TRAINER:
        trainer = get_linked_trainer(request.user)
        clients = clients.filter(trainer=trainer)
    elif role == UserProfile.ROLE_CLIENT:
        client = get_linked_client(request.user)
        clients = clients.filter(id=client.id if client else None)
    return clients


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION, UserProfile.ROLE_TRAINER)
def client_list(request):
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'todos')
    
    clients = _get_role_scoped_clients(request).order_by('-join_date')
    
    if search_query:
        clients = clients.filter(
            models.Q(first_name__icontains=search_query) | 
            models.Q(last_name__icontains=search_query) | 
            models.Q(ci__icontains=search_query)
        )
    
    if status_filter == 'activos':
        clients = clients.filter(is_active=True)
    elif status_filter == 'inactivos':
        clients = clients.filter(is_active=False)
        
    context = {
        'clients': clients,
        'search_query': search_query,
        'status_filter': status_filter
    }
    return render(request, 'clients/client_list.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def client_create(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        ci = request.POST.get('ci')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        height_cm = request.POST.get('height_cm')
        weight_kg = request.POST.get('weight_kg')
        profile_photo = request.FILES.get('profile_photo')
        
        # Handle empty strings for numeric fields
        height_cm = height_cm if height_cm else None
        weight_kg = weight_kg if weight_kg else None
        
        try:
            client = Client.objects.create(
                first_name=first_name,
                last_name=last_name,
                ci=ci,
                phone=phone,
                email=email,
                height_cm=height_cm,
                weight_kg=weight_kg,
                profile_photo=profile_photo
            )
            
            if height_cm and weight_kg:
                PhysicalDataHistory.objects.create(
                    client=client,
                    height_cm=height_cm,
                    weight_kg=weight_kg
                )
                
            messages.success(request, 'Cliente registrado correctamente.')
            return redirect('client_detail', client_id=client.id)
        except Exception as e:
            messages.error(request, f'Error al registrar cliente: {e}')
            return render(request, 'clients/client_form.html')
    
    return render(request, 'clients/client_form.html')


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def client_edit(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        client.first_name = request.POST.get('first_name')
        client.last_name = request.POST.get('last_name')
        client.ci = request.POST.get('ci')
        client.phone = request.POST.get('phone')
        client.email = request.POST.get('email')
        
        new_height = request.POST.get('height_cm')
        new_weight = request.POST.get('weight_kg')
        
        # Handle empty strings
        new_height = new_height if new_height else None
        new_weight = new_weight if new_weight else None
        
        if str(new_height) != str(client.height_cm) or str(new_weight) != str(client.weight_kg):
            if new_height and new_weight:
                PhysicalDataHistory.objects.create(
                    client=client,
                    height_cm=new_height,
                    weight_kg=new_weight
                )
        
        client.height_cm = new_height
        client.weight_kg = new_weight
        
        if request.FILES.get('profile_photo'):
            client.profile_photo = request.FILES.get('profile_photo')
            
        client.is_active = request.POST.get('is_active') == 'on'
        client.save()
        
        messages.success(request, 'Cliente actualizado correctamente.')
        return redirect('client_detail', client_id=client.id)
    
    return render(request, 'clients/client_form.html', {'client': client})


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION, UserProfile.ROLE_TRAINER, UserProfile.ROLE_CLIENT)
def client_detail(request, client_id):
    client = get_object_or_404(_get_role_scoped_clients(request), id=client_id)
    memberships = client.memberships.all().order_by('-start_date')
    payments = client.payments.all().order_by('-date')
    physical_history = client.physical_history.all().order_by('-date')

    physical_history_rows = []
    for item in physical_history:
        bmi = None
        try:
            if item.height_cm and item.weight_kg:
                height_m = Decimal(item.height_cm) / Decimal('100')
                if height_m != 0:
                    bmi = round(Decimal(item.weight_kg) / (height_m * height_m), 1)
        except (InvalidOperation, ZeroDivisionError):
            bmi = None

        physical_history_rows.append({
            'item': item,
            'bmi': bmi,
        })
    
    context = {
        'client': client,
        'memberships': memberships,
        'payments': payments,
        'physical_history': physical_history,
        'physical_history_rows': physical_history_rows,
    }
    return render(request, 'clients/client_detail.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def client_delete(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Cliente eliminado correctamente.')
        return redirect('client_list')
    return redirect('client_detail', client_id=client_id)
