from dateutil.relativedelta import relativedelta

from django.test import TestCase, tag
from model_mommy import mommy

from edc_constants.constants import YES

from ..constants import NO_HOUSEHOLD_INFORMANT
from ..exceptions import HouseholdAssessmentError
from ..forms import HouseholdAssessmentForm

from .mixin import HouseholdMixin


class TestForms(HouseholdMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.household_structure = self.make_household_structure(
            household_status=NO_HOUSEHOLD_INFORMANT)

    @tag('me1')
    def test_household_assessment_not_required_if_enumerated(self):
        household_structure = self.make_household_structure()
        mommy.make_recipe(
            'member.representativeeligibility',
            household_structure=household_structure,
            report_datetime=self.get_utcnow())
#         mommy.make_recipe(
#             'member.householdmember',
#             household_structure=household_structure,
#             report_datetime=self.get_utcnow(),
#             )
#         self.assertRaises(
#             HouseholdAlreadyEnumeratedError,
#             mommy.make_recipe,
#             'household.householdassessment',
#             household_structure=household_structure,
#             report_datetime=self.get_utcnow())

    @tag('me')
    def test_household_assessment_not_required_if_insufficient_attempts(self):
        self.assertRaises(
            HouseholdAssessmentError,
            mommy.make_recipe,
            'household.householdassessment',
            household_structure=self.household_structure,
            report_datetime=self.get_utcnow())

    @tag('me')
    def test_household_assessment_potential_eligibles_yes(self):
        """Assert if eligibles_last_seen_home is not answered
        potential_eligibles is yes, error is raised."""

        household_structure = self.make_household_structure(
            attempts=1,
            household_status=NO_HOUSEHOLD_INFORMANT,
            report_datetime=self.get_utcnow() + relativedelta(days=1))

        household_structure = self.add_failed_enumeration_attempt(
            household_structure, household_status=NO_HOUSEHOLD_INFORMANT)
        household_structure = self.add_failed_enumeration_attempt(
            household_structure, household_status=NO_HOUSEHOLD_INFORMANT)

        self.assertGreaterEqual(household_structure.enumeration_attempts, 3)

        data = dict(
            household_structure=self.household_structure.id,
            report_datetime=self.get_utcnow() + relativedelta(days=2),
            potential_eligibles=YES,
            eligibles_last_seen_home=None)

        form = HouseholdAssessmentForm(data)
        self.assertFalse(form.is_valid())
