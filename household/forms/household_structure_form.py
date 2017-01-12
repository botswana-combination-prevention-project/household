from django import forms

from ..models import HouseholdStructure


class HouseholdStructureForm(forms.ModelForm):

    # TODO: verify it is not possible to edit data from surveys other than the current

    class Meta:
        model = HouseholdStructure
        fields = '__all__'
