from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist

from .models import RoleSlot, ShipRoleTemplate


def _ordered_user_queryset():
    """Return the list of users ordered by their username field."""

    user_model = get_user_model()
    order_field = getattr(user_model, "USERNAME_FIELD", "username")
    try:
        user_model._meta.get_field(order_field)
    except FieldDoesNotExist:
        order_field = "pk"
    return user_model.objects.order_by(order_field)


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
        queryset=get_user_model().objects.none(),
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
        self.fields["user"].queryset = user_queryset or _ordered_user_queryset()
        self.fields["user"].empty_label = "— Libre —"

    @staticmethod
    def default_user_queryset():
        return _ordered_user_queryset()
