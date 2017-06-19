from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_map.site_mappers import site_mappers
from survey.tests import SurveyTestHelper

from ..constants import ELIGIBLE_REPRESENTATIVE_ABSENT
from ..model_wrappers import HouseholdLogEntryModelWrapper, HouseholdModelWrapper
from ..model_wrappers import HouseholdStructureModelWrapper
from ..model_wrappers import HouseholdStructureWithLogEntryWrapper
from ..models import HouseholdLogEntry
from .household_test_helper import HouseholdTestHelper
from .mappers import TestMapper


@tag('wrappers')
class TestWrappers(TestCase):

    household_helper = HouseholdTestHelper()
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)
        self.household_structure = self.household_helper.make_household_structure()

    def test_household_log_entry_model_wrapper(self):
        model_obj = HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
        wrapper = HouseholdLogEntryModelWrapper(model_obj=model_obj)
        self.assertIsNotNone(wrapper.href)

    def test_household_model_wrapper(self):
        wrapper = HouseholdModelWrapper(
            model_obj=self.household_structure.household)
        self.assertIsNotNone(wrapper.href)

    def test_household_structure_model_wrapper(self):
        wrapper = HouseholdStructureModelWrapper(
            model_obj=self.household_structure)
        self.assertIsNotNone(wrapper.href)

    @tag('1')
    def test_household_structure_with_log_entry_model_wrapper_href1(self):
        wrapper = HouseholdStructureWithLogEntryWrapper(
            model_obj=self.household_structure)
        self.assertIsNotNone(wrapper.href)

    @tag('1')
    def test_household_structure_with_log_entry_model_wrapper_href2(self):
        wrapper = HouseholdStructureWithLogEntryWrapper(
            model_obj=self.household_structure)
        self.assertIn(
            'next=household_dashoard:listboard_url,', wrapper.href)

    @tag('1')
    def test_household_structure_with_log_entry_model_wrapper_href3(self):
        wrapper = HouseholdStructureWithLogEntryWrapper(
            model_obj=self.household_structure)
        household_identifier = self.household_structure.household.household_identifier
        self.assertIn(
            f'household_identifier={household_identifier}', wrapper.href)

    @tag('1')
    def test_household_structure_with_log_entry_model_wrapper_href4(self):
        wrapper = HouseholdStructureWithLogEntryWrapper(
            model_obj=self.household_structure)
        survey_schedule = self.household_structure.survey_schedule_object.field_value
        self.assertIn(
            f'survey_schedule={survey_schedule}', wrapper.href)

    @tag('1')
    def test_household_structure_with_log_entry_model_wrapper_href5(self):
        wrapper = HouseholdStructureWithLogEntryWrapper(
            model_obj=self.household_structure)
        plot_identifier = self.household_structure.household.plot.plot_identifier
        self.assertIn(
            f'plot_identifier={plot_identifier}', wrapper.href)

    @tag('1')
    def test_household_structure_with_log_entry_model_wrapper_log_models(self):
        wrapper = HouseholdStructureWithLogEntryWrapper(
            model_obj=self.household_structure)
        self.assertIsNotNone(wrapper.log)
        self.assertIsNotNone(wrapper.log_model)

    @tag('1')
    def test_household_structure_with_log_entry_model_wrapper_log_entry_models(self):
        wrapper = HouseholdStructureWithLogEntryWrapper(
            model_obj=self.household_structure)
        self.assertIsNotNone(wrapper.log_entry)
        self.assertIsNotNone(wrapper.log_entry_model)
        self.assertIsNotNone(wrapper.log_entries)

    def test_household_structure_with_log_entry_model_wrapper2(self):
        HouseholdLogEntry.objects.create(
            household_log=self.household_structure.householdlog,
            household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
        wrapper = HouseholdStructureWithLogEntryWrapper(
            model_obj=self.household_structure)
        self.assertIsNotNone(wrapper.href)
