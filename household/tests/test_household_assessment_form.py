from django.test import TestCase, tag
from django.utils import timezone

from edc_constants.constants import YES

from ..constants import NO_HOUSEHOLD_INFORMANT
from ..forms import HouseholdAssessmentForm

from .test_mixins import HouseholdMixin
from dateutil.relativedelta import relativedelta


class TestHouseholdAssessmentForm(HouseholdMixin, TestCase):

    def setUp(self):
        super(TestHouseholdAssessmentForm, self).setUp()
        self.household_log_entries = self.make_household_with_household_log_entry(
            household_status=NO_HOUSEHOLD_INFORMANT)
        if self.household_log_entries:
            log_entry = self.household_log_entries[0]
            self.household_log = log_entry.household_log
            self.household_structure = log_entry.household_log.household_structure
        self.data = {
            'household_structure': self.household_structure.id,
            'report_datetime': timezone.now(),
            'potential_eligibles': YES,
            'eligibles_last_seen_home': None}

    def test_potential_eligibles_yes(self):
        """Assert if eligibles_last_seen_home is not answered potential_eligibles is yes, error is raised."""
        self.make_household_log_entry(
            household_log=self.household_log,
            household_status=NO_HOUSEHOLD_INFORMANT,
            report_datetime=self.get_utcnow())
        self.make_household_log_entry(
            household_log=self.household_log,
            household_status=NO_HOUSEHOLD_INFORMANT,
            report_datetime=self.get_utcnow() + relativedelta(hours=1))
        self.assertEqual(self.household_structure.enumeration_attempts, 3)
        form = HouseholdAssessmentForm(data=self.data)
        self.assertFalse(form.is_valid())
        errors = ''.join(form.errors.get('__all__'))
        self.assertIn('Question 2 must be answered when question 1 answer is Yes.', errors)
