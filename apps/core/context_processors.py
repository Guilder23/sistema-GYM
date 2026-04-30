from apps.notifications.models import Notification


def notifications_count(request):
    if not request.user.is_authenticated:
        return {'notifications_count': 0}

    count = Notification.objects.filter(sent=True, is_read=False).count()
    return {'notifications_count': count}
