from django import forms

from edc_constants.constants import OTHER

from ..models import HouseholdRefusal
from ..exceptions import FormNotRequiredError, HouseholdAlreadyEnrolledError


class HouseholdRefusalForm(forms.ModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('reason') == OTHER:
            raise forms.ValidationError("If other for the question above please answer question 3.")
        try:
            instance = self._meta.model(id=self.instance.id, **cleaned_data)
            instance.common_clean()
        except (FormNotRequiredError, HouseholdAlreadyEnrolledError) as e:
            raise forms.ValidationError(str(e))
        return cleaned_data

    class Meta:
        model = HouseholdRefusal
        fields = '__all__'
