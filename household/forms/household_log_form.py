from django import forms

from ..models import HouseholdLog


class HouseholdLogForm(forms.ModelForm):

    class Meta:
        model = HouseholdLog
        fields = '__all__'
