from django.apps import apps as django_apps
from django import forms

from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_base.modelform_validators import FormValidator

from ..constants import REFUSED_ENUMERATION
from ..models import HouseholdLogEntry


class HouseholdLogEntryFormValidator(FormValidator):
    def __init__(self, max_enumeration_attempts=None, is_current_schedule=None, **kwargs):
        super().__init__(**kwargs)
        app_config = django_apps.get_app_config('household')
        household_log = self.cleaned_data.get('household_log')
        household_status = self.cleaned_data.get('household_status')
        if household_status == REFUSED_ENUMERATION:
            self.refused_enumeration = True
        else:
            self.refused_enumeration = False
        self.enumerated = household_log.household_structure.enumerated
        self.current_schedule = (
            household_log.household_structure.survey_schedule_object.field_value)
        if is_current_schedule is not None:
            self.is_current_schedule = is_current_schedule
        else:
            self.is_current_schedule = (
                household_log.household_structure.survey_schedule_object.current)
        self.enumeration_attempts = household_log.household_structure.enumeration_attempts
        self.max_enumeration_attempts = (
            max_enumeration_attempts or app_config.max_enumeration_attempts)

    def clean(self):
        if not self.instance.id:
            # cannot refuse if already enumerated
            if self.refused_enumeration and self.enumerated:
                raise forms.ValidationError({
                    'household_status': 'Invalid selection. Household has been enumerated'})
            # cannot add if not current survey schedule
            elif not self.is_current_schedule:
                raise forms.ValidationError(
                    f'{self.instance._meta.verbose_name} may only be created '
                    f'for the current survey. Got {self.current_schedule}.',
                    code='survey_schedule')
            # cannot add if beyond the limit
            elif self.max_enumeration_attempts > 0:
                if self.enumeration_attempts >= self.max_enumeration_attempts:
                    raise forms.ValidationError(
                        'Maximum number of enumeration attempts already met. '
                        f'Got {self.enumeration_attempts}.', code='enumeration_attempts')

        self.require_together(
            field='next_appt_datetime',
            field_required='next_appt_datetime_source')


class HouseholdLogEntryForm(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        form_validator = HouseholdLogEntryFormValidator(
            cleaned_data=cleaned_data,
            instance=self.instance)
        form_validator.validate()
        return cleaned_data

    class Meta:
        model = HouseholdLogEntry
        fields = '__all__'
