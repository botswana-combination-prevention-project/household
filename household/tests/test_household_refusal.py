from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_map.site_mappers import site_mappers
from survey.tests import SurveyTestHelper

from ..models import HouseholdLogEntry, HouseholdStructure
from .household_test_helper import HouseholdTestHelper
from .mappers import TestMapper
from household.constants import REFUSED_ENUMERATION
from household.models.household_refusal import HouseholdRefusal


@tag('1')
class TestHouseholdRefusal(TestCase):

    household_helper = HouseholdTestHelper()
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)
        self.household_structure = self.household_helper.make_household_structure()

    @property
    def requeried_household_structure(self):
        return HouseholdStructure.objects.get(id=self.household_structure.id)

    def test_refused(self):
        HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=REFUSED_ENUMERATION)
        self.assertFalse(
            self.requeried_household_structure.refused_enumeration)

    def test_refused_log_entry_does_not_update_household_structure(self):
        HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=REFUSED_ENUMERATION)
        self.assertFalse(
            self.requeried_household_structure.refused_enumeration)

    def test_updates_household_structure(self):
        HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=REFUSED_ENUMERATION)
        HouseholdRefusal.objects.create(
            household_structure=self.household_structure)
        self.assertTrue(
            self.requeried_household_structure.refused_enumeration)

    def test_delete_updates_household_structure(self):
        HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=REFUSED_ENUMERATION)
        obj = HouseholdRefusal.objects.create(
            household_structure=self.household_structure)
        obj.delete()
        self.assertFalse(
            self.requeried_household_structure.refused_enumeration)
