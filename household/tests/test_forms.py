from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.test import TestCase, tag
from model_mommy import mommy

from edc_constants.constants import YES, OTHER
from edc_map.site_mappers import site_mappers

from ..constants import NO_HOUSEHOLD_INFORMANT
from ..exceptions import HouseholdAssessmentError
from ..forms import HouseholdAssessmentForm, HouseholdRefusalForm
from ..models import HouseholdStructure
from .household_test_helper import HouseholdTestHelper, get_utcnow
from .mappers import TestMapper


@tag('forms')
class TestForms(TestCase):

    household_helper = HouseholdTestHelper()

    def setUp(self):
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)
        self.household_structure = self.household_helper.make_household_structure(
            household_status=NO_HOUSEHOLD_INFORMANT)

#     def test_household_assessment_not_required_if_enumerated(self):
#         self.fail('representativeeligibility')
#         household_structure = self.household_helper.make_household_structure()
#         mommy.make_recipe(
#             'member.representativeeligibility',
#             household_structure=household_structure,
#             report_datetime=get_utcnow())

    def test_household_assessment_not_required_if_insufficient_attempts(self):
        self.assertRaises(
            HouseholdAssessmentError,
            mommy.make_recipe,
            'household.householdassessment',
            household_structure=self.household_structure,
            report_datetime=get_utcnow())

    def test_household_assessment_potential_eligibles_yes(self):
        """Assert if eligibles_last_seen_home is not answered
        potential_eligibles is yes, error is raised."""

        household_structure = self.household_helper.make_household_structure(
            attempts=1,
            household_status=NO_HOUSEHOLD_INFORMANT,
            report_datetime=get_utcnow() + relativedelta(days=1))

        household_structure = self.household_helper.add_failed_enumeration_attempt(
            household_structure, household_status=NO_HOUSEHOLD_INFORMANT)
        household_structure = self.household_helper.add_failed_enumeration_attempt(
            household_structure, household_status=NO_HOUSEHOLD_INFORMANT)

        self.assertGreaterEqual(household_structure.enumeration_attempts, 3)

        data = dict(
            household_structure=self.household_structure.id,
            report_datetime=get_utcnow() + relativedelta(days=2),
            potential_eligibles=YES,
            eligibles_last_seen_home=None)

        form = HouseholdAssessmentForm(data)
        self.assertFalse(form.is_valid())

    def test_household_assessment_form(self):
        plot = self.household_helper.make_confirmed_plot(household_count=1)
        household = plot.household_set.all()[0]
        household_structure = household.householdstructure_set.all()[0]
        household_structure.enumerated = False
        household_structure.failed_enumeration_attempts = 3
        household_structure.save()
        household_structure = HouseholdStructure.objects.get(
            id=household_structure.id)
        self.assertEqual(household_structure.failed_enumeration_attempts, 3)
        data = dict(
            household_structure=household_structure.id,
            report_datetime=get_utcnow() + relativedelta(days=2),
            potential_eligibles=YES,
            eligibles_last_seen_home=None)

        form = HouseholdAssessmentForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('eligibles_last_seen_home', form.errors)

    def test_household_refusal_form(self):
        plot = self.household_helper.make_confirmed_plot(household_count=1)
        household = plot.household_set.all()[0]
        household_structure = household.householdstructure_set.all()[0]
        data = dict(
            household_structure=household_structure.id,
            report_datetime=get_utcnow() + relativedelta(days=2),
            reason=OTHER,
            reason_other=None)
        form = HouseholdRefusalForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('reason_other', form.errors)
