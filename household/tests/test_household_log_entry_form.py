from django import forms
from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_base.utils import get_utcnow
from edc_map.site_mappers import site_mappers

from ..constants import REFUSED_ENUMERATION
from ..forms import HouseholdLogEntryFormValidator
from ..models import HouseholdStructure, HouseholdLogEntry
from .household_test_helper import HouseholdTestHelper
from .mappers import TestMapper
from household.forms.household_log_entry_form import HouseholdLogEntryForm
from household.constants import ELIGIBLE_REPRESENTATIVE_PRESENT,\
    ELIGIBLE_REPRESENTATIVE_ABSENT
from dateutil.relativedelta import relativedelta


@tag('forms')
class TestHouseholdLogEntryForm(TestCase):

    household_helper = HouseholdTestHelper()

    def setUp(self):
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)
        self.household_structure = self.household_helper.make_household_structure()

    def test_form_validator_next_appt_datetime1(self):
        household_log = self.household_structure.householdlog
        cleaned_data = {
            'household_log': self.household_structure.householdlog,
            'next_appt_datetime': get_utcnow() + relativedelta(weeks=1)}
        form_validator = HouseholdLogEntryFormValidator(
            cleaned_data=cleaned_data,
            instance=HouseholdLogEntry(household_log=household_log))
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('next_appt_datetime_source', form_validator._errors)

    def test_form_validator_next_appt_datetime2(self):
        household_log = self.household_structure.householdlog
        cleaned_data = {
            'household_log': self.household_structure.householdlog,
            'next_appt_datetime': None,
            'next_appt_datetime_source': 'household member'}
        form_validator = HouseholdLogEntryFormValidator(
            cleaned_data=cleaned_data,
            instance=HouseholdLogEntry(household_log=household_log))
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('next_appt_datetime_source', form_validator._errors)

    def test_form_validator_household_status(self):
        self.household_structure.enumerated = True
        self.household_structure.save()
        household_structure = HouseholdStructure.objects.get(
            id=self.household_structure.id)
        household_log = household_structure.householdlog
        cleaned_data = {
            'household_log': household_structure.householdlog,
            'household_status': REFUSED_ENUMERATION}
        form_validator = HouseholdLogEntryFormValidator(
            cleaned_data=cleaned_data,
            instance=HouseholdLogEntry(household_log=household_log))
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('household_status', form_validator._errors)

    def test_form_validator_max_household_log_entries(self):
        self.household_structure.enumeration_attempts = 100
        self.household_structure.save()
        household_structure = HouseholdStructure.objects.get(
            id=self.household_structure.id)
        household_log = household_structure.householdlog
        cleaned_data = {
            'household_log': household_structure.householdlog}
        form_validator = HouseholdLogEntryFormValidator(
            max_enumeration_attempts=1,
            cleaned_data=cleaned_data,
            instance=HouseholdLogEntry(household_log=household_log))
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('enumeration_attempts', form_validator._error_codes)

    @tag('1')
    def test_form_validator_current_schedule(self):
        household_structure = HouseholdStructure.objects.get(
            id=self.household_structure.id)
        household_log = household_structure.householdlog
        cleaned_data = {
            'household_log': household_structure.householdlog}
        form_validator = HouseholdLogEntryFormValidator(
            is_current_schedule=False,
            cleaned_data=cleaned_data,
            instance=HouseholdLogEntry(household_log=household_log))
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('survey_schedule', form_validator._error_codes)

    def test_form_report_datetime1(self):
        data = {
            'household_log': self.household_structure.householdlog.id,
            'report_datetime': get_utcnow()}
        form = HouseholdLogEntryForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.get('report_datetime'), None)

    def test_form_report_datetime2(self):
        data = {
            'household_log': self.household_structure.householdlog.id,
            'report_datetime': get_utcnow() + relativedelta(weeks=1)}
        form = HouseholdLogEntryForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.get('report_datetime'), ['Cannot be a future date'])

    def test_form_next_appt_datetime1(self):
        data = {
            'household_log': self.household_structure.householdlog.id,
            'household_status': ELIGIBLE_REPRESENTATIVE_ABSENT,
            'next_appt_datetime': get_utcnow() + relativedelta(weeks=1),
            'next_appt_datetime_source': 'household member'}
        form = HouseholdLogEntryForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.get('next_appt_datetime'), None)

    def test_form_next_appt_datetime2(self):
        data = {
            'household_log': self.household_structure.householdlog.id,
            'household_status': ELIGIBLE_REPRESENTATIVE_ABSENT,
            'next_appt_datetime': get_utcnow(),
            'next_appt_datetime_source': 'household member'}
        form = HouseholdLogEntryForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.get('next_appt_datetime'), ['Expected a future date'])
