from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(sent=True).order_by('-created_at')
    context = {'notifications': notifications}
    return render(request, 'notifications/notification_list.html', context)
