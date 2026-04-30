from django.contrib import admin
from .models import ClassType, ClassSchedule, Reservation

@admin.register(ClassType)
class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('class_type', 'date', 'start_time', 'end_time', 'capacity', 'trainer')
    list_filter = ('date', 'class_type')
    search_fields = ('class_type__name', 'trainer__full_name')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('client', 'schedule', 'reserved_at', 'confirmed')
    list_filter = ('confirmed', 'schedule__date')
    search_fields = ('client__first_name', 'client__last_name')
