from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_map.site_mappers import site_mappers
from survey.tests import SurveyTestHelper

from ..constants import ELIGIBLE_REPRESENTATIVE_ABSENT, ELIGIBLE_REPRESENTATIVE_PRESENT
from ..models import HouseholdLogEntry, HouseholdStructure
from .household_test_helper import HouseholdTestHelper
from .mappers import TestMapper


class TestHouseholdLogEntry(TestCase):

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

    def test_create_keeps_enumeration_count(self):
        HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
        self.assertEqual(
            self.requeried_household_structure.enumeration_attempts, 1)
        self.assertEqual(
            self.requeried_household_structure.failed_enumeration_attempts, 1)

    def test_create_keeps_enumeration_count2(self):
        HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT)
        self.assertEqual(
            self.requeried_household_structure.enumeration_attempts, 1)
        self.assertEqual(
            self.requeried_household_structure.failed_enumeration_attempts, 0)

    @tag('2')
    def test_updates_failed_enumeration(self):
        for _ in range(0, 3):
            HouseholdLogEntry.objects.create(
                household_log=self.household_structure.householdlog,
                household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
        self.assertEqual(
            self.requeried_household_structure.failed_enumeration_attempts, 3)

        # failed_enumeration is only updated by HouseholdAssessment
        self.assertFalse(
            self.requeried_household_structure.failed_enumeration)

    def test_delete_updates_enumeration_counts(self):
        obj = HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
        obj.delete()
        self.assertEqual(
            self.requeried_household_structure.enumeration_attempts, 0)
        self.assertEqual(
            self.requeried_household_structure.failed_enumeration_attempts, 0)

    def test_delete_updates_enumeration_counts2(self):
        HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT)
        obj = HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
        obj.delete()
        self.assertEqual(
            self.requeried_household_structure.enumeration_attempts, 1)
        self.assertEqual(
            self.requeried_household_structure.failed_enumeration_attempts, 0)

    def test_delete_updates_enumeration_counts3(self):
        for _ in range(0, 2):
            HouseholdLogEntry.objects.create(
                household_log=self.household_structure.householdlog,
                household_status=ELIGIBLE_REPRESENTATIVE_PRESENT)
        self.assertEqual(
            self.requeried_household_structure.enumeration_attempts, 2)
        obj = HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
        self.assertEqual(
            self.requeried_household_structure.enumeration_attempts, 3)
        obj.delete()
        self.assertEqual(
            self.requeried_household_structure.enumeration_attempts, 2)
        self.assertEqual(
            self.requeried_household_structure.failed_enumeration_attempts, 0)

    def test_invalid_attempts_count_recovers(self):
        obj = HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT)
        self.household_structure.enumeration_attempts = -1
        self.household_structure.save()
        self.assertEqual(
            self.requeried_household_structure.enumeration_attempts, -1)
        obj.delete()
        self.assertEqual(
            self.requeried_household_structure.enumeration_attempts, 0)

    def test_invalid_failed_attempts_count_recovers(self):
        obj = HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
        self.household_structure.failed_enumeration_attempts = -1
        self.household_structure.save()
        self.assertEqual(
            self.requeried_household_structure.failed_enumeration_attempts, -1)
        obj.delete()
        self.assertEqual(
            self.requeried_household_structure.failed_enumeration_attempts, 0)
