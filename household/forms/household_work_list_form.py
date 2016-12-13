from django import forms

from ..models import HouseholdWorkList


class HouseholdWorkListForm(forms.ModelForm):

    class Meta:
        model = HouseholdWorkList
        fields = '__all__'
