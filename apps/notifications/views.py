from django.shortcuts import render
from .models import Notification
from apps.core.models import UserProfile
from apps.core.permissions import get_linked_client, get_user_role, role_required


@role_required(
    UserProfile.ROLE_ADMIN,
    UserProfile.ROLE_RECEPTION,
    UserProfile.ROLE_TRAINER,
    UserProfile.ROLE_CLIENT,
)
def notification_list(request):
    notifications = Notification.objects.filter(sent=True).order_by('-created_at')
    if get_user_role(request.user) == UserProfile.ROLE_CLIENT:
        notifications = notifications.filter(recipient=get_linked_client(request.user))
    context = {'notifications': notifications}
    return render(request, 'notifications/notification_list.html', context)
