from django import forms

from edc_constants.constants import YES

from ..models import HouseholdAssessment
from ..exceptions import HouseholdAssessmentError, HouseholdAlreadyEnumeratedError


class HouseholdAssessmentForm(forms.ModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data

        if cleaned_data.get('potential_eligibles') == YES and cleaned_data.get('eligibles_last_seen_home') is None:
            raise forms.ValidationError('Question 2 must be answered when question 1 answer is Yes.')
        try:
            instance = self._meta.model(id=self.instance.id, **cleaned_data)
            instance.common_clean()
        except (HouseholdAlreadyEnumeratedError, HouseholdAssessmentError) as e:
            raise forms.ValidationError(str(e))
        return cleaned_data

    class Meta:
        model = HouseholdAssessment
        fields = '__all__'
