from django import forms

from edc_base.modelform_validators import FormValidator
from edc_base.modelform_mixins import CommonCleanModelFormMixin

from ..models import HouseholdRefusal


class HouseholdRefusalFormValidator(FormValidator):

    def clean(self):
        self.validate_other_specify(field='reason')


class HouseholdRefusalForm(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        form_validator = HouseholdRefusalFormValidator(
            cleaned_data=cleaned_data)
        form_validator.validate()
        return cleaned_data

    class Meta:
        model = HouseholdRefusal
        fields = '__all__'
