from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_map.site_mappers import site_mappers

from survey.site_surveys import site_surveys
from survey.tests import SurveyTestHelper

from .household_test_helper import HouseholdTestHelper
from .mappers import TestMapper


@tag('survey')
class TestSurvey(TestCase):

    """Tests to assert survey attrs.
    """

    household_helper = HouseholdTestHelper()
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys(load_all=True)
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)

    def test_household_structure(self):
        survey_schedule = site_surveys.get_survey_schedules()[0]
        household_structure = self.household_helper.make_household_structure(
            survey_schedule=survey_schedule)

        self.assertIsNotNone(household_structure.survey_schedule)
        self.assertIsNotNone(household_structure.survey_schedule_object)
        self.assertRaises(
            AttributeError, getattr, household_structure, 'survey')
        self.assertRaises(
            AttributeError, getattr, household_structure, 'survey_object')

    def test_household_structure_survey_schedule_set_correctly(self):

        survey_schedules = site_surveys.get_survey_schedules(
            group_name='test_survey', current=True)

        if not survey_schedules:
            raise AssertionError('survey_schedules is unexpectedly None')

        for index, survey_schedule in enumerate(survey_schedules):
            household_structure = self.household_helper.make_household_structure(
                survey_schedule=survey_schedule)
            self.assertEqual(
                household_structure.survey_schedule,
                f'test_survey.year-{index + 1}.test_community')
            self.assertEqual(
                household_structure.survey_schedule_object.field_value,
                f'test_survey.year-{index + 1}.test_community')
            self.assertEqual(
                household_structure.survey_schedule_object.name,
                f'year-{index + 1}')
            self.assertEqual(
                household_structure.survey_schedule_object.group_name,
                'test_survey')
            self.assertEqual(
                household_structure.survey_schedule_object.short_name,
                f'test_survey.year-{index + 1}')
