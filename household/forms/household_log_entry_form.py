import arrow

from django.apps import apps as django_apps
from django import forms

from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_base.utils import get_utcnow

from ..constants import REFUSED_ENUMERATION
from ..models import HouseholdLogEntry


class HouseholdLogEntryForm(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super(HouseholdLogEntryForm, self).clean()

        if not self.instance.id:
            household_log = self.cleaned_data.get('household_log')
            household_identifier = household_log.household_structure.household.household_identifier
            HouseholdMember = django_apps.get_model('member.householdmember')
            household_member = HouseholdMember.objects.filter(
                household_identifier=household_identifier)
            if (household_member
                    and self.cleaned_data.get(
                        'household_status') == REFUSED_ENUMERATION):
                raise forms.ValidationError(
                    'Cannot refuse enumeration as household has existing'
                    ' members.')

            if not household_log.household_structure.survey_schedule_object.current:
                raise forms.ValidationError(
                    '{} may only be created for the current survey. '
                    'Got {}.'.format(
                        self._meta.model._meta.verbose_name,
                        household_log.household_structure.survey_schedule_object.field_value))
            app_config = django_apps.get_app_config('household')
            # only allow x instances, set in app_config, set to zero to bypass
            if app_config.max_household_log_entries:
                count = self._meta.model.objects.filter(
                    household_log=household_log).count()
                if count >= app_config.max_household_log_entries:
                    raise forms.ValidationError(
                        'Maximum number of enumeration attempts already met. {}'
                        ' is not required. Got {}.'.format(
                            self._meta.model._meta.verbose_name, count))

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
        if (cleaned_data.get('next_appt_datetime')
                and not cleaned_data.get('next_appt_datetime_source')):
            raise forms.ValidationError(
                {'next_appt_datetime_source': 'Required with appointment'})
        if (not cleaned_data.get('next_appt_datetime')
                and cleaned_data.get('next_appt_datetime_source')):
            raise forms.ValidationError(
                {'next_appt_datetime_source': 'Not required without appointment'})
        return cleaned_data

    class Meta:
        model = HouseholdLogEntry
        fields = '__all__'
