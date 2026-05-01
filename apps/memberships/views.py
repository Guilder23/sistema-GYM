import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import MembershipPlan, Membership, Payment
from apps.clients.models import Client
from datetime import datetime, timedelta
from apps.core.models import UserProfile
from apps.core.permissions import get_linked_client, get_user_role, role_required


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def membership_plans(request):
    plans = MembershipPlan.objects.all()
    context = {'plans': plans}
    return render(request, 'memberships/plan_list.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def membership_plan_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        duration_days = request.POST.get('duration_days', 30)
        price = request.POST.get('price', 0)
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, 'El nombre del plan es obligatorio.')
            return render(request, 'memberships/plan_form.html')
        
        MembershipPlan.objects.create(
            name=name,
            duration_days=int(duration_days),
            price=float(price),
            description=description
        )

        messages.success(request, 'Plan de membresía creado correctamente.')
        return redirect('plan_list')
    
    return render(request, 'memberships/plan_form.html')


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def membership_for_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    plans = MembershipPlan.objects.filter(active=True).order_by('duration_days', 'price')
    
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        method = request.POST.get('method', 'EFECTIVO')
        plan = get_object_or_404(MembershipPlan, id=plan_id)
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=int(plan.duration_days))
        
        membership = Membership.objects.create(
            client=client,
            plan=plan,
            start_date=start_date,
            end_date=end_date
        )
        
        Payment.objects.create(
            client=client,
            membership=membership,
            amount=plan.price,
            method=method,
            receipt_code=uuid.uuid4().hex[:10].upper(),
        )

        messages.success(request, 'Membresía asignada y pago registrado correctamente.')
        return redirect('client_detail', client_id=client.id)
    
    context = {'client': client, 'plans': plans}
    return render(request, 'memberships/assign_membership.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def payment_history(request):
    payments = Payment.objects.all().order_by('-date')
    context = {'payments': payments}
    return render(request, 'memberships/payment_history.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def payment_create(request):
    clients = Client.objects.filter(is_active=True).order_by('first_name', 'last_name')

    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        amount = request.POST.get('amount')
        method = request.POST.get('method', 'EFECTIVO')
        notes = request.POST.get('notes', '').strip()

        if not client_id or not amount:
            messages.error(request, 'Cliente y monto son obligatorios.')
            return render(request, 'memberships/payment_form.html', {'clients': clients})

        client = get_object_or_404(Client, id=client_id)
        membership = client.memberships.order_by('-start_date').first()

        receipt_code = uuid.uuid4().hex[:10].upper()
        Payment.objects.create(
            client=client,
            membership=membership,
            amount=amount,
            method=method,
            receipt_code=receipt_code,
            notes=notes,
        )

        messages.success(request, 'Pago registrado correctamente.')
        return redirect('payment_list')

    return render(request, 'memberships/payment_form.html', {'clients': clients})


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION, UserProfile.ROLE_CLIENT)
def payment_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if get_user_role(request.user) == UserProfile.ROLE_CLIENT:
        client = get_linked_client(request.user)
        if not client or payment.client != client:
            messages.error(request, 'No tienes permisos para ver este comprobante.')
            return redirect('dashboard')

    return render(request, 'memberships/payment_receipt.html', {'payment': payment})
