# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account
from profiles.models import Customer  # Import Customer model

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    def delete_model(self, request, obj):
        # Delete related customers first
        Customer.objects.filter(user=obj).delete()
        # Then delete the account
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        # For bulk deletion
        for obj in queryset:
            Customer.objects.filter(user=obj).delete()
        super().delete_queryset(request, queryset)

admin.site.register(Account, AccountAdmin)