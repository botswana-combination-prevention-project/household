from django import forms

from ..models import HouseholdStructure


class HouseholdStructureForm(forms.ModelForm):

    class Meta:
        model = HouseholdStructure
        fields = '__all__'
