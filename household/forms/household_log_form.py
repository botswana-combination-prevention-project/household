import datetime

from django import forms

from ..models import HouseholdLog, HouseholdLogEntry


class HouseholdLogForm(forms.ModelForm):

    class Meta:
        model = HouseholdLog
        fields = '__all__'


class HouseholdLogEntryForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(HouseholdLogEntryForm, self).clean()
        # confirm next_appt_datetime to a future time
        if cleaned_data.get('next_appt_datetime'):
            if not cleaned_data.get('next_appt_datetime') >= datetime.datetime.now():
                raise forms.ValidationError(
                    'The next appointment date must be on or after the report '
                    'datetime. You entered {0}'.format(
                        cleaned_data.get('next_appt_datetime').strftime('%Y-%m-%d')))
        if cleaned_data.get('next_appt_datetime') and not cleaned_data.get('next_appt_datetime_source'):
            raise forms.ValidationError({'next_appt_datetime_source': 'Required with appointment'})
        if not cleaned_data.get('next_appt_datetime') and cleaned_data.get('next_appt_datetime_source'):
            raise forms.ValidationError({'next_appt_datetime_source': 'Not required without appointment'})
        return cleaned_data

    class Meta:
        model = HouseholdLogEntry
        fields = '__all__'
