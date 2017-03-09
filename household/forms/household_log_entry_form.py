import arrow

from django.apps import apps as django_apps
from django import forms

from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_base.utils import get_utcnow

from ..models import HouseholdLogEntry, HouseholdLog
from household.constants import REFUSED_ENUMERATION


class HouseholdLogEntryForm(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super(HouseholdLogEntryForm, self).clean()

        if not self.instance.id:
            household_log = self.cleaned_data.get('household_log')
            previous_structure = household_log.household_structure.previous
            previous_household_log = HouseholdLog.objects.filter(
                household_structure=previous_structure).order_by('report_datetime').last()
            previous_log_entry = HouseholdLogEntry.objects.filter(
                household_log=previous_household_log).order_by('report_datetime').last()
            if(previous_log_entry.household_status and
                (self.cleaned_data.get('household_status') == REFUSED_ENUMERATION
                 and previous_log_entry.household_status != REFUSED_ENUMERATION)):
                raise forms.ValidationError(
                    'Cannot refuse enumeration as household has been'
                    ' previously enumerated.')

            if not household_log.household_structure.survey_schedule_object.current:
                raise forms.ValidationError(
                    '{} may only be created for the current survey. Got {}.'.format(
                        self._meta.model._meta.verbose_name,
                        household_log.household_structure.survey_schedule_object.field_value))
            app_config = django_apps.get_app_config('household')
            # only allow x instances, set in app_config, set to zero to bypass
            if app_config.max_household_log_entries:
                count = self._meta.model.objects.filter(
                    household_log=household_log).count()
                if count >= app_config.max_household_log_entries:
                    raise forms.ValidationError(
                        'Maximum number of enumeration attempts already met. {} is not '
                        'required. Got {}.'.format(self._meta.model._meta.verbose_name, count))

        # confirm next_appt_datetime to a future time
        report_datetime = cleaned_data.get('next_appt_datetime')
        if report_datetime:
            rdate = arrow.Arrow.fromdatetime(
                report_datetime, report_datetime.tzinfo)
            if rdate.to('utc') <= get_utcnow():
                raise forms.ValidationError(
                    'The next appointment date must be on or after the report '
                    'datetime. You entered {0}'.format(
                        cleaned_data.get('next_appt_datetime').strftime('%Y-%m-%d')))
        if cleaned_data.get('next_appt_datetime') and not cleaned_data.get('next_appt_datetime_source'):
            raise forms.ValidationError(
                {'next_appt_datetime_source': 'Required with appointment'})
        if not cleaned_data.get('next_appt_datetime') and cleaned_data.get('next_appt_datetime_source'):
            raise forms.ValidationError(
                {'next_appt_datetime_source': 'Not required without appointment'})
        return cleaned_data

    class Meta:
        model = HouseholdLogEntry
        fields = '__all__'
