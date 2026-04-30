from django.contrib import admin
from .models import Trainer

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialty', 'phone', 'email', 'active')
    list_filter = ('active',)
    search_fields = ('full_name', 'specialty')
