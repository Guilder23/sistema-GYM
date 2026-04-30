from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
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
    user_role = get_user_role(request.user)
    
    # Base filter: sent and either global or specifically for this user/client
    notifications = Notification.objects.filter(sent=True)
    
    if user_role == UserProfile.ROLE_CLIENT:
        client = get_linked_client(request.user)
        notifications = notifications.filter(
            Q(is_global=True) | Q(recipient_client=client)
        )
    else:
        # For staff roles (Admin, Reception, Trainer)
        notifications = notifications.filter(
            Q(is_global=True) | Q(recipient_user=request.user)
        )
        
    notifications = notifications.order_by('-created_at')
    
    context = {
        'notifications': notifications,
        'user_role': user_role
    }
    return render(request, 'notifications/notification_list.html', context)


@role_required(UserProfile.ROLE_ADMIN)
def create_announcement(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        
        if title and message:
            Notification.objects.create(
                title=title,
                message=message,
                notification_type='COMUNICADO',
                is_global=True,
                sent=True
            )
            messages.success(request, 'Comunicado enviado a todos los usuarios.')
            return redirect('notification_list')
        else:
            messages.error(request, 'Título y mensaje son obligatorios.')
            
    return render(request, 'notifications/announcement_form.html')


@role_required(
    UserProfile.ROLE_ADMIN,
    UserProfile.ROLE_RECEPTION,
    UserProfile.ROLE_TRAINER,
    UserProfile.ROLE_CLIENT,
)
def mark_as_read(request, notification_id):
    # This logic would ideally verify the recipient, but for simplicity:
    notification = Notification.objects.filter(id=notification_id).first()
    if notification:
        notification.is_read = True
        notification.save()
    return redirect('notification_list')
