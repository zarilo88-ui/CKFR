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
