from django import forms

from edc_base.modelform_validators import FormValidator
from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_constants.constants import YES

from ..models import HouseholdAssessment


class HouseholdAssessmentFormValidator(FormValidator):

    def clean(self):
        self.required_if(
            YES, field='potential_eligibles',
            field_required='eligibles_last_seen_home')


class HouseholdAssessmentForm(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        form_validator = HouseholdAssessmentFormValidator(
            cleaned_data=cleaned_data)
        form_validator.validate()
        return cleaned_data

    class Meta:
        model = HouseholdAssessment
        fields = '__all__'
