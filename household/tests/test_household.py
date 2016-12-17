from django.test import TestCase

from ..models import HouseholdStructure

from .test_mixins import HouseholdMixin
from survey.models import Survey


class TestHousehold(HouseholdMixin, TestCase):

    def test_creates_household_structure(self):
        plot = self.make_confirmed_plot(household_count=2)
        self.assertEqual(Survey.objects.all().count(), 3)
        self.assertEqual(HouseholdStructure.objects.filter(household__plot=plot), 3)

    def test_cannot_delete_household_with_household_log(self):
        plot = self.make_confirmed_plot(household_count=2)
        self.make_household_log_entry()
