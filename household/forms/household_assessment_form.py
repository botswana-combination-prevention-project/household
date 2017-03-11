from django import forms

from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_constants.constants import YES

from ..models import HouseholdAssessment


class HouseholdAssessmentForm(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data
        if (cleaned_data.get('potential_eligibles') == YES and
                not cleaned_data.get('eligibles_last_seen_home')):
            raise forms.ValidationError({
                'eligibles_last_seen_home': 'This field is required.'})
        return cleaned_data

    class Meta:
        model = HouseholdAssessment
        fields = '__all__'
