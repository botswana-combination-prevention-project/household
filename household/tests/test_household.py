from django.test import TestCase

from ..models import HouseholdStructure

from .test_mixins import HouseholdMixin
from household.models.household import Household
from household.models.household_log import HouseholdLog
from django.db.models.deletion import ProtectedError
from household.models.household_log_entry import HouseholdLogEntry


class TestHousehold(HouseholdMixin, TestCase):

    def test_creates_household_structure(self):
        """Asserts household structure instances are created when households are created."""
        plot = self.make_confirmed_plot(household_count=2)
        # each household needs 3 household_structures
        # based on example_survey.surveys and survey.AppConfig
        self.assertEqual(HouseholdStructure.objects.filter(household__plot=plot).count(), 6)

    def test_deletes_household_structure(self):
        """Asserts deletes household structure instances households are deleted."""
        plot = self.make_confirmed_plot(household_count=2)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 2)
        for household in Household.objects.filter(plot=plot):
            self.assertEqual(HouseholdStructure.objects.filter(household=household).count(), 3)
        plot.household_count = 1
        plot.save()
        self.assertEqual(Household.objects.filter(plot=plot).count(), 1)
        for household in Household.objects.filter(plot=plot):
            self.assertEqual(HouseholdStructure.objects.filter(household=household).count(), 3)

    def test_cannot_delete_household_with_household_log_entry(self):
        plot = self.make_confirmed_plot(household_count=5)
        # create a household_log_entry for each 
        for household_structure in HouseholdStructure.objects.filter(household__plot=plot):
            household_log = HouseholdLog.objects.get(household_structure=household_structure)
            self.make_household_log_entry(household_log=household_log)
        self.assertEqual(HouseholdLogEntry.objects.filter(
            household_log__household_structure__household__plot=plot).count(), 15)
        
        plot.household_count = 1
        plot.save()
        self.assertEqual(HouseholdLogEntry.objects.filter(
            household_log__household_structure__household__plot=plot).count(), 1)

    def test_can_delete_household_without_household_log_entry(self):
        plot = self.make_confirmed_plot(household_count=2)
        for household_structure in HouseholdStructure.objects.filter(household__plot=plot):
            household_log = HouseholdLog.objects.get(household_structure=household_structure)
            household = household_log.household_structure.household
            try:
                household.delete()
            except ProtectedError:
                self.fail('ProtectedError unexpectedly raised.')
