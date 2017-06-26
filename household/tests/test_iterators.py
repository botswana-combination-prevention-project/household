# coding=utf-8

from django.apps import apps as django_apps
from django.test import TestCase, tag
from edc_map.site_mappers import site_mappers

from survey.tests import SurveyTestHelper

from ..iterators import HouseholdStructureIterator
from ..models import HouseholdStructure
from .household_test_helper import HouseholdTestHelper
from .mappers import TestMapper


@tag('iterators')
class TestIterators(TestCase):

    household_helper = HouseholdTestHelper()
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys(load_all=True)
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)

    def test_iterator(self):
        household_structure = self.household_helper.make_household_structure()
        iterator = HouseholdStructureIterator(
            household=household_structure.household)
        self.assertEqual(
            list(iterator),
            list(household_structure.household.householdstructure_set.all().order_by(
                'report_datetime')))

    def test_iterator_for(self):
        plot = self.household_helper.make_confirmed_plot(household_count=1)
        household = plot.household_set.all()[0]
        HouseholdStructure.objects.create(
            household=household, survey_schedule=f'test_survey.year-2.test_community')
        HouseholdStructure.objects.create(
            household=household, survey_schedule=f'test_survey.year-3.test_community')
        iterator = HouseholdStructureIterator(
            household=household)
        for index, hs in enumerate(iterator):
            self.assertEqual(
                hs.survey_schedule,
                f'test_survey.year-{index + 1}.test_community')

    def test_iterator_reverse(self):
        plot = self.household_helper.make_confirmed_plot(household_count=3)
        household = plot.household_set.all()[0]
        self.household_helper.make_household_structure()
        HouseholdStructure.objects.create(
            household=household, survey_schedule=f'test_survey.year-2.test_community')
        HouseholdStructure.objects.create(
            household=household, survey_schedule=f'test_survey.year-3.test_community')
        iterator = HouseholdStructureIterator(
            household=household)
        for index, hs in enumerate(reversed(list(iterator))):
            self.assertEqual(
                hs.survey_schedule,
                f'test_survey.year-{abs(index - 3)}.test_community')
