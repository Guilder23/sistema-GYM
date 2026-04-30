from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from .models import SystemSetting
from apps.clients.models import Client
from apps.memberships.models import Membership, Payment
from apps.access.models import AccessRecord
from apps.reservations.models import Reservation, ClassSchedule
from apps.inventory.models import Product
from apps.notifications.models import Notification


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Credenciales inválidas. Intenta de nuevo.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    clients_count = Client.objects.count()
    active_memberships_count = Membership.objects.filter(active=True).count()
    last_payments = Payment.objects.order_by('-date')[:5]
    recent_access = AccessRecord.objects.order_by('-timestamp')[:5]
    upcoming_classes = ClassSchedule.objects.filter(date__gte=timezone.now().date()).order_by('date', 'start_time')[:5]
    products_low_stock = Product.objects.filter(stock__lte=models.F('min_stock'))
    notifications = Notification.objects.filter(sent=True).order_by('-created_at')[:4]

    active_clients = Client.objects.filter(is_active=True).count()
    inactive_clients = Client.objects.filter(is_active=False).count()

    context = {
        'clients_count': clients_count,
        'active_memberships_count': active_memberships_count,
        'last_payments': last_payments,
        'recent_access': recent_access,
        'upcoming_classes': upcoming_classes,
        'products_low_stock': products_low_stock,
        'notifications': notifications,
        'active_clients': active_clients,
        'inactive_clients': inactive_clients,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
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
