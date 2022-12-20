from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (None, {"fields": ("first_name", "last_name", "email")}),
        (
            None,
            {
                "fields": (
                    "is_active",
                    "is_staff",
                ),
            },
        ),
        (None, {"fields": ("last_login", "date_joined")}),
    )

    # list page
    list_display = ("username", "email", "first_name", "last_name")
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    # user page
    readonly_fields = ('last_login', 'date_joined')
    exclude = ['password']

    def get_form(self, request, obj=None, **kwargs):
        is_superuser = request.user.is_superuser
        disabled_fields = set()
        defaults = {}

        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)

        if not is_superuser:
            disabled_fields |= {
                'username',
                'is_superuser',
            }
        for field in disabled_fields:
            if field in self.form.base_fields:
                self.form.base_fields[field].disabled = True

        return super().get_form(request, obj, **defaults)
