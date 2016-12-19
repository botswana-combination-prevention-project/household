from model_mommy import mommy

from edc_base.test_mixins import ReferenceDateMixin, LoadListDataMixin

from plot.test_mixins import PlotMixin
from survey.site_surveys import site_surveys

from ..constants import (
    ELIGIBLE_REPRESENTATIVE_PRESENT, ELIGIBLE_REPRESENTATIVE_ABSENT, NO_HOUSEHOLD_INFORMANT,
    UNKNOWN_OCCUPIED)
from ..exceptions import EnumerationAttemptsExceeded
from ..models import HouseholdLog, HouseholdStructure, HouseholdLogEntry, is_no_informant


class HouseholdTestMixin(PlotMixin, LoadListDataMixin):

    list_data = None  # list_data


class HouseholdMixin(ReferenceDateMixin, HouseholdTestMixin):

    def setUp(self):
        super(HouseholdMixin, self).setUp()
        self.study_site = '40'

    def make_household_log_entry(self, household_log, household_status=None, **options):
        return mommy.make_recipe(
            'household.householdlogentry',
            household_log=household_log,
            household_status=household_status,
            **options)

    def make_household_refusal(self, household_log_entry=None, household_structure=None):
        if household_log_entry:
            household_structure = household_log_entry.household_log.household_structure
        mommy.make_recipe(
            'household.householdrefusal',
            household_structure=household_structure)

    def make_household_with_household_log_entry(self, household_status=None, survey_name=None):
        household_status = household_status or ELIGIBLE_REPRESENTATIVE_PRESENT
        survey_name = survey_name or 'example-survey'
        surveys = [survey for survey in site_surveys.surveys if survey_name in survey.survey_schedule]
        plot = self.make_confirmed_plot(household_count=1)
        household_structures = HouseholdStructure.objects.filter(household__plot=plot, survey__in=surveys)
        for household_structure in household_structures:
            household_log = HouseholdLog.objects.get(household_structure=household_structure)
            self.make_household_log_entry(household_log=household_log, household_status=household_status)
        household_log_entrys = HouseholdLogEntry.objects.filter(
            household_log__household_structure=household_structure)
        return household_log_entrys

    def make_household_with_max_enumeration_attempts(self, household_log=None, household_status=None):
        """Returns household_structure after adding three unsuccessful enumeration attempts,
        or as many as are still needed."""
        household_status = household_status or ELIGIBLE_REPRESENTATIVE_ABSENT
        household_log_entrys = None
        if household_log:
            household_log_entrys = HouseholdLogEntry.objects.filter(household_log=household_log)
        if not household_log_entrys:
            household_log_entrys = self.make_household_with_household_log_entry(
                household_status=household_status)
        household_log = household_log_entrys[0].household_log
        household_structure = HouseholdStructure.objects.get(
            pk=household_log.household_structure.pk)
        self.assertEqual(household_structure.enumeration_attempts, 1)
        max_attempts_reached = False
        for _ in range(0, 10):  # should break after three exist
            try:
                self.make_household_log_entry(
                    household_log=household_log, household_status=household_status)
            except EnumerationAttemptsExceeded:
                max_attempts_reached = True
                break
        self.assertTrue(max_attempts_reached)
        household_structure = HouseholdStructure.objects.get(
            pk=household_log.household_structure.pk)
        self.assertEqual(household_structure.enumeration_attempts, 3)
        self.assertEqual(HouseholdLogEntry.objects.filter(household_log=household_log).count(), 3)
        return household_structure

    def make_household_failed_enumeration_with_household_assessment(
            self, household_status=None, eligibles_last_seen_home=None):
        household_status = household_status or NO_HOUSEHOLD_INFORMANT
        eligibles_last_seen_home = eligibles_last_seen_home or UNKNOWN_OCCUPIED
        household_structure = self.make_household_with_max_enumeration_attempts(
            household_status=household_status)
        household_structure = HouseholdStructure.objects.get(
            pk=household_structure.pk)
        household_assessment = mommy.make_recipe(
            'household.householdassessment',
            household_structure=household_structure,
            eligibles_last_seen_home=eligibles_last_seen_home)
        household_structure = HouseholdStructure.objects.get(
            pk=household_structure.pk)
        self.assertTrue(household_structure.failed_enumeration)
        self.assertEqual(household_structure.no_informant, is_no_informant(household_assessment))
        return household_structure
