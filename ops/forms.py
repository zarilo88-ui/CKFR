from django import forms
from django.contrib.auth.models import User
from .models import Ship, ShipRoleTemplate, RoleSlot

class ShipForm(forms.ModelForm):
    class Meta:
        model = Ship
        fields = ("name", "min_crew", "max_crew")

class ShipRoleTemplateForm(forms.ModelForm):
    class Meta:
        model = ShipRoleTemplate
        fields = ("role_name", "slots")

class RoleSlotForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        label="Utilisateur",
        queryset=User.objects.order_by("username"),
        required=False
    )
    class Meta:
        model = RoleSlot
        fields = ("user", "status")
