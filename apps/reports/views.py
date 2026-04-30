from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.clients.models import Client
from apps.memberships.models import Payment, Membership
from apps.access.models import AccessRecord
from apps.inventory.models import Sale
from datetime import datetime, timedelta


@login_required
def reports_dashboard(request):
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    total_revenue_month = sum(p.amount for p in Payment.objects.filter(date__gte=month_ago))
    active_clients = Client.objects.filter(is_active=True).count()
    inactive_clients = Client.objects.filter(is_active=False).count()
    today_access = AccessRecord.objects.filter(timestamp__date=today).count()
    
    context = {
        'total_revenue_month': total_revenue_month,
        'active_clients': active_clients,
        'inactive_clients': inactive_clients,
        'today_access': today_access,
    }
    return render(request, 'reports/dashboard.html', context)
