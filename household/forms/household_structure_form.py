from django import forms

from ..models import HouseholdStructure
from household.exceptions import HouseholdEnumerationError


class HouseholdStructureForm(forms.ModelForm):

    # TODO: verify it is not possible to edit data from surveys other than the current

    def clean(self):
        cleaned_data = super().clean()
        try:
            instance = self._meta.model(id=self.instance.id, **cleaned_data)
            instance.common_clean()
        except HouseholdEnumerationError as e:
            raise forms.ValidationError(str(e))
        return cleaned_data

    class Meta:
        model = HouseholdStructure
        fields = '__all__'
