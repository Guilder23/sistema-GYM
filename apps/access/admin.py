from django.contrib import admin
from .models import AccessRecord

@admin.register(AccessRecord)
class AccessRecordAdmin(admin.ModelAdmin):
    list_display = ('client', 'timestamp', 'entry_type', 'method', 'valid')
    list_filter = ('entry_type', 'method', 'valid')
    search_fields = ('client__first_name', 'client__last_name')
