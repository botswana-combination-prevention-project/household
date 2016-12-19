from django.test import TestCase, tag

from ..models import HouseholdStructure

from .test_mixins import HouseholdMixin
from household.models.household import Household
from household.models.household_log import HouseholdLog
from household.models.household_log_entry import HouseholdLogEntry
from plot.models import Plot
from household.constants import NO_HOUSEHOLD_INFORMANT, ELIGIBLE_REPRESENTATIVE_ABSENT, REFUSED_ENUMERATION,\
    ELIGIBLE_REPRESENTATIVE_PRESENT
from household.models.household_refusal import HouseholdRefusal


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
            household_log__household_structure__household__plot=plot).count(), 15)
        plot = Plot.objects.get(pk=plot.pk)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 5)

    def test_cannot_only_delete_households_without_household_log_entry(self):
        plot = self.make_confirmed_plot(household_count=5)
        # create a household_log_entry for some
        for household in Household.objects.filter(plot=plot)[0:2]:
            for household_structure in HouseholdStructure.objects.filter(household=household):
                household_log = HouseholdLog.objects.get(household_structure=household_structure)
                self.make_household_log_entry(household_log=household_log)
        self.assertEqual(HouseholdLogEntry.objects.filter(
            household_log__household_structure__household__plot=plot).count(), 6)
        plot.household_count = 1
        plot.save()
        self.assertEqual(HouseholdLogEntry.objects.filter(
            household_log__household_structure__household__plot=plot).count(), 6)
        plot = Plot.objects.get(pk=plot.pk)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 3)

    def test_can_delete_household_without_household_log_entry(self):
        plot = self.make_confirmed_plot(household_count=2)
        plot.household_count = 1
        plot.save()
        self.assertEqual(Household.objects.filter(plot=plot).count(), 1)

    def test_household_with_refused_enumeration_by_log_entry(self):
        household_log_entrys = self.make_household_with_log_entry(household_status=REFUSED_ENUMERATION)
        for household_log_entry in household_log_entrys:
            self.assertEqual(household_log_entry.household_log.last_log_status, REFUSED_ENUMERATION)
            self.assertEqual(household_log_entry.household_log.household_structure.failed_enumeration_attempts, 1)
            self.assertFalse(household_log_entry.household_log.household_structure.refused_enumeration)

    def test_household_with_refused_enumeration_confirmed(self):
        household_log_entrys = self.make_household_with_log_entry(household_status=REFUSED_ENUMERATION)
        for household_log_entry in household_log_entrys:
            self.make_household_refusal(household_log_entry=household_log_entry)
            self.assertEqual(household_log_entry.household_log.household_structure.failed_enumeration_attempts, 1)
            self.assertTrue(household_log_entry.household_log.household_structure.refused_enumeration)

    def test_delete_refused_enumeration_confirmed_updates_household_structure(self):
        household_log_entrys = self.make_household_with_log_entry(household_status=REFUSED_ENUMERATION)
        for household_log_entry in household_log_entrys:
            self.make_household_refusal(household_log_entry=household_log_entry)
        HouseholdRefusal.objects.all().delete()
        household_log_entrys = HouseholdLogEntry.objects.filter(household_log=household_log_entry.household_log)
        for household_log_entry in household_log_entrys:
            self.assertEqual(household_log_entry.household_log.household_structure.failed_enumeration_attempts, 1)
            self.assertFalse(household_log_entry.household_log.household_structure.refused_enumeration)

    def test_household_with_no_informant(self):
        household_log_entrys = self.make_household_with_log_entry(household_status=NO_HOUSEHOLD_INFORMANT)
        for household_log_entry in household_log_entrys:
            self.assertEqual(household_log_entry.household_log.last_log_status, NO_HOUSEHOLD_INFORMANT)

    def test_household_with_no_representative(self):
        household_log_entrys = self.make_household_with_log_entry(household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
        for household_log_entry in household_log_entrys:
            self.assertEqual(household_log_entry.household_log.last_log_status, ELIGIBLE_REPRESENTATIVE_ABSENT)

    def test_household_with_representative(self):
        self.make_household_with_log_entry(household_status=ELIGIBLE_REPRESENTATIVE_PRESENT)

    def test_household_log_entry_updates_household_log_last_log_status(self):
        household_log_entrys = self.make_household_with_log_entry(household_status=NO_HOUSEHOLD_INFORMANT)
        for household_log_entry in household_log_entrys:
            self.assertEqual(household_log_entry.household_log.last_log_status, NO_HOUSEHOLD_INFORMANT)
        for household_log_entry in household_log_entrys:
            household_log_entry.household_status = ELIGIBLE_REPRESENTATIVE_ABSENT
            household_log_entry.save()
            household_log_entry = HouseholdLogEntry.objects.get(pk=household_log_entry.pk)
            self.assertEqual(household_log_entry.household_log.last_log_status, ELIGIBLE_REPRESENTATIVE_ABSENT)
        for household_log_entry in household_log_entrys:
            household_log_entry.household_status = REFUSED_ENUMERATION
            household_log_entry.save()
            household_log_entry = HouseholdLogEntry.objects.get(pk=household_log_entry.pk)
            self.assertEqual(household_log_entry.household_log.last_log_status, REFUSED_ENUMERATION)
        for household_log_entry in household_log_entrys:
            household_log_entry.household_status = ELIGIBLE_REPRESENTATIVE_PRESENT
            household_log_entry.save()
            household_log_entry = HouseholdLogEntry.objects.get(pk=household_log_entry.pk)
            self.assertEqual(household_log_entry.household_log.last_log_status, ELIGIBLE_REPRESENTATIVE_PRESENT)
