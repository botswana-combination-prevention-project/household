from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_map.site_mappers import site_mappers
from survey.tests import SurveyTestHelper

from ..exceptions import HouseholdAlreadyEnumeratedError
from ..models import HouseholdStructure, HouseholdAssessment
from .household_test_helper import HouseholdTestHelper
from .mappers import TestMapper


@tag('models')
class TestHouseholdAssessment(TestCase):

    household_helper = HouseholdTestHelper()
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)

    def test_create_household_assessment(self):
        plot = self.household_helper.make_confirmed_plot(household_count=1)
        household_structure = HouseholdStructure.objects.filter(
            household__plot=plot)[0]
        household_structure.enumerated = False
        household_structure.failed_enumeration_attempts = 3
        obj = HouseholdAssessment.objects.create(
            household_structure=household_structure)
        self.assertTrue(str(obj))

    def test_household_assessment_natural_key(self):
        plot = self.household_helper.make_confirmed_plot(household_count=1)
        household_structure = HouseholdStructure.objects.filter(
            household__plot=plot)[0]
        household_structure.enumerated = False
        household_structure.failed_enumeration_attempts = 3
        obj = HouseholdAssessment.objects.create(
            household_structure=household_structure)
        self.assertEqual(obj.natural_key(), household_structure.natural_key())

    def test_household_assessment_updates_failed_enumeration(self):
        plot = self.household_helper.make_confirmed_plot(household_count=1)
        household_structure = HouseholdStructure.objects.filter(
            household__plot=plot)[0]
        household_structure.enumerated = False
        household_structure.failed_enumeration_attempts = 3
        household_structure.save()
        HouseholdAssessment.objects.create(
            household_structure=household_structure)
        household_structure = HouseholdStructure.objects.get(
            id=household_structure.id)
        self.assertTrue(household_structure.failed_enumeration)

    def test_cannot_create_household_assessment_if_enumerated(self):
        plot = self.household_helper.make_confirmed_plot(household_count=1)
        household_structure = HouseholdStructure.objects.filter(
            household__plot=plot)[0]
        household_structure.enumerated = True
        household_structure.save()
        self.assertRaises(
            HouseholdAlreadyEnumeratedError,
            HouseholdAssessment.objects.create,
            household_structure=household_structure)

    def test_household_delete_household_assessment1(self):
        """Assert harmlessly tries deletes HouseholdAssessment
        if not enumerated where HouseholdAssessment does not exist.
        """
        plot = self.household_helper.make_confirmed_plot(household_count=1)
        household_structure = HouseholdStructure.objects.filter(
            household__plot=plot)[0]
        household_structure.enumerated = True
        self.assertIsNone(household_structure.save())

    def test_household_delete_household_assessment2(self):
        """Assert deletes HouseholdAssessment if enumerated.

        Error raised in the signal.
        """
        plot = self.household_helper.make_confirmed_plot(household_count=1)
        household_structure = HouseholdStructure.objects.filter(
            household__plot=plot)[0]
        self.assertFalse(household_structure.enumerated)

        household_structure.failed_enumeration_attempts = 3
        household_structure.save()
        HouseholdAssessment.objects.create(
            household_structure=household_structure)

        household_structure.enumerated = True
        household_structure.save()
        self.assertRaises(
            HouseholdAssessment.DoesNotExist,
            HouseholdAssessment.objects.get,
            household_structure=household_structure)
