from django.contrib import admin
from .models import MembershipPlan, Membership, Payment

@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'price')
    search_fields = ('name',)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('client', 'plan', 'start_date', 'end_date', 'active')
    list_filter = ('active',)
    search_fields = ('client__first_name', 'client__last_name')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('client', 'membership', 'amount', 'date', 'method')
    search_fields = ('client__first_name', 'client__last_name', 'receipt_code')
