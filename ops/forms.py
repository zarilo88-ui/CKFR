from django import forms
from django.contrib.auth import get_user_model

from .models import ShipRoleTemplate, RoleSlot
from .utils import get_ordered_user_queryset


class ShipRoleTemplateForm(forms.ModelForm):
    class Meta:
        model = ShipRoleTemplate
        fields = ("role_name", "slots")
        widgets = {
            "role_name": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/10 bg-white/5 text-white px-3 py-2",
                    "placeholder": "Rôle",
                }
            ),
            "slots": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/10 bg-white/5 text-white px-3 py-2",
                    "min": 1,
                }
            ),
        }


class RoleSlotForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        label="Utilisateur",
        queryset=get_user_model()._default_manager.none(),
        required=False,
    )

    class Meta:
        model = RoleSlot
        fields = ("user", "status")
        widgets = {
            "user": forms.Select(
                attrs={
                    "class": "w-full rounded-xl border border-white/15 bg-black/40 px-3 py-2",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full rounded-xl border border-white/15 bg-black/40 px-3 py-2",
                }
            ),
        }

    def __init__(self, *args, user_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = user_queryset or get_ordered_user_queryset()
        self.fields["user"].queryset = qs
        self.fields["user"].empty_label = "— Libre —"

    @staticmethod
    def default_user_queryset():
        return get_ordered_user_queryset()
