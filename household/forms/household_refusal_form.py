from django import forms

from edc_constants.constants import OTHER

from ..exceptions import FormNotRequiredError, HouseholdAlreadyEnrolledError
from ..models import HouseholdRefusal


class HouseholdRefusalForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('reason') == OTHER:
            raise forms.ValidationError(
                "If other for the question above please answer question 3.")
        try:
            instance = self._meta.model(id=self.instance.id, **cleaned_data)
            instance.common_clean()
        except (FormNotRequiredError, HouseholdAlreadyEnrolledError) as e:
            raise forms.ValidationError(str(e))
        return cleaned_data

    class Meta:
        model = HouseholdRefusal
        fields = '__all__'
