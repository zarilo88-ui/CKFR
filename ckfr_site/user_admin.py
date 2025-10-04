from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms

# Always show ******** instead of the hashed password block
class MaskedPasswordWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return "********"

class CustomUserChangeForm(forms.ModelForm):
    # Override the password field to prevent ReadOnlyPasswordHashField
    password = forms.CharField(label="Mot de passe", required=False, widget=MaskedPasswordWidget())

    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "is_staff" in self.fields:
            self.fields["is_staff"].label = "Admin"
        if "is_superuser" in self.fields:
            self.fields["is_superuser"].label = "SuperAdmin"

# Unregister the default admin first (avoids AlreadyRegistered)
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    # keep default layouts
    fieldsets = BaseUserAdmin.fieldsets
    add_fieldsets = BaseUserAdmin.add_fieldsets

    def _protect_superadmin(self, request, obj=None) -> bool:
        return bool(obj) and getattr(obj, "is_superuser", False) and not request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        if self._protect_superadmin(request, obj):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if self._protect_superadmin(request, obj):
            return False
        return super().has_delete_permission(request, obj)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser and "delete_selected" in actions:
            del actions["delete_selected"]
        return actions