from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import UserProfile


ROLE_LABELS = {
    UserProfile.ROLE_ADMIN: 'Administrador',
    UserProfile.ROLE_RECEPTION: 'Recepcionista',
    UserProfile.ROLE_TRAINER: 'Entrenador',
    UserProfile.ROLE_CLIENT: 'Cliente',
}


def get_user_profile(user):
    if not user or not user.is_authenticated:
        return None
    default_role = UserProfile.ROLE_ADMIN if user.is_superuser else UserProfile.ROLE_RECEPTION
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': default_role},
    )
    if user.is_superuser and profile.role != UserProfile.ROLE_ADMIN:
        profile.role = UserProfile.ROLE_ADMIN
        profile.save(update_fields=['role'])
    return profile


def get_user_role(user):
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser:
        return UserProfile.ROLE_ADMIN
    profile = get_user_profile(user)
    return profile.role if profile else None


def get_role_label(role):
    return ROLE_LABELS.get(role, 'Sin rol')


def get_linked_client(user):
    profile = get_user_profile(user)
    return profile.client if profile else None


def get_linked_trainer(user):
    profile = get_user_profile(user)
    return profile.trainer if profile else None


def has_role(user, *allowed_roles):
    role = get_user_role(user)
    return role in allowed_roles


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if has_role(request.user, *allowed_roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('dashboard')

        return wrapped_view

    return decorator
