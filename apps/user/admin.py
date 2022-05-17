from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


# Register your models here.


class CustomUserAdmin(UserAdmin):
    search_fields = ('phone', 'email')
    list_filter = ('is_active', 'is_phone_verified')
    list_display = ('email', 'phone', 'last_login', 'date_joined',
                    'is_active', 'is_phone_verified')
    date_hierarchy = ('last_login')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', ('password1', 'password2'))
        }),
    )
    fieldsets = (
        (None, {
            'fields': ('email', 'phone', 'password')
        }),

        ('more options', {
            'classes': ('collapse',),
            'fields':  ('first_name', 'last_name'),
        }),
    )

    save_on_top =True

    list_editable = ('is_active',)

    ordering = ()

admin.site.register(CustomUser, CustomUserAdmin)