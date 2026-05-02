from apps.notifications.models import Notification
from .permissions import get_linked_client, get_linked_trainer, get_role_label, get_user_role


def notifications_count(request):
    if not request.user.is_authenticated:
        return {
            'notifications_count': 0,
            'current_user_role': None,
            'current_user_role_label': '',
            'linked_client': None,
            'linked_trainer': None,
        }

    current_user_role = get_user_role(request.user)
    linked_client = get_linked_client(request.user)
    linked_trainer = get_linked_trainer(request.user)

    from django.db.models import Q
    notifications = Notification.objects.filter(sent=True)
    
    if current_user_role == 'CLIENTE' and linked_client:
        notifications = notifications.filter(
            Q(is_global=True) | Q(recipient_client=linked_client)
        )
    else:
        notifications = notifications.filter(
            Q(is_global=True) | Q(recipient_user=request.user)
        )

    count = notifications.filter(is_read=False).count()
    recent_notifications = notifications.order_by('-created_at')[:5]

    return {
        'notifications_count': count,
        'recent_notifications': recent_notifications,
        'current_user_role': current_user_role,
        'current_user_role_label': get_role_label(current_user_role),
        'linked_client': linked_client,
        'linked_trainer': linked_trainer,
    }
