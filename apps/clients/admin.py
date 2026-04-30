from django.contrib import admin
from .models import Client, Attendance

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'ci', 'phone', 'is_active')
    search_fields = ('first_name', 'last_name', 'ci', 'phone')
    list_filter = ('is_active',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('client', 'check_in', 'method', 'valid')
    list_filter = ('method', 'valid')
    search_fields = ('client__first_name', 'client__last_name', 'note')
