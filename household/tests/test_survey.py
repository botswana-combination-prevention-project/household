from django.test import TestCase, tag

from survey.site_surveys import site_surveys
from survey.tests import SurveyTestHelper

from .household_test_helper import HouseholdTestHelper


class TestSurvey(TestCase):

    """Tests to assert survey attrs.
    """

    household_helper = HouseholdTestHelper()
    survey_helper = SurveyTestHelper()

    def test_household_structure(self):
        self.survey_schedule = self.survey_helper.get_survey_schedule(0)
        self.household_structure = self.household_helper.make_household_structure(
            survey_schedule=self.survey_schedule)

        self.assertIsNotNone(self.household_structure.survey_schedule)
        self.assertIsNotNone(self.household_structure.survey_schedule_object)
        self.assertRaises(
            AttributeError, getattr, self.household_structure, 'survey')
        self.assertRaises(
            AttributeError, getattr, self.household_structure, 'survey_object')

    def test_household_structure_survey_schedule_set_correctly(self):

        survey_schedules = site_surveys.get_survey_schedules(
            group_name='test_survey')

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
