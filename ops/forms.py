from django import forms
from django.contrib.auth.models import User
from .models import Operation, OperationShip, Assignment

class OperationForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = ("title","start","description")

class OperationShipForm(forms.ModelForm):
    class Meta:
        model = OperationShip
        fields = ("ship","notes")

class AssignmentForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.order_by("username"), required=False)
    class Meta:
        model = Assignment
        fields = ("user","status")
