from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from django.db import transaction
from django.db.utils import IntegrityError

from edc_base_test.mixins import LoadListDataMixin

from plot.tests import PlotMixin
from survey.site_surveys import site_surveys

from ..constants import (
    ELIGIBLE_REPRESENTATIVE_PRESENT, ELIGIBLE_REPRESENTATIVE_ABSENT, NO_HOUSEHOLD_INFORMANT,
    UNKNOWN_OCCUPIED)
from ..exceptions import EnumerationAttemptsExceeded
from ..models import HouseholdLog, HouseholdStructure, HouseholdLogEntry, is_no_informant
from edc_base_test.exceptions import TestMixinError


class HouseholdTestMixin(PlotMixin, LoadListDataMixin):

    list_data = None  # list_data


class HouseholdMixin(HouseholdTestMixin):

    def setUp(self):
        super().setUp()
        self.study_site = '40'

    def make_household_log_entry(self, household_log, household_status=None, **options):
        """Makes an householdlogentry instance.

        Note: you need to increment report datetime if making multiple instances."""
        options.update(report_datetime=options.get('report_datetime', self.get_utcnow()))
        return mommy.make_recipe(
            'household.householdlogentry',
            household_log=household_log,
            household_status=household_status,
            **options)

    def make_household_assessment(self, household_structure, **options):
        options.update(report_datetime=options.get('report_datetime', self.get_utcnow()))
        return mommy.make_recipe(
            'household.householdassessment',
            household_structure=household_structure,
            **options)

    def make_household_refusal(self, household_log_entry=None, household_structure=None):
        if household_log_entry:
            household_structure = household_log_entry.household_log.household_structure
        mommy.make_recipe(
            'household.householdrefusal',
            report_datetime=self.get_utcnow(),
            household_structure=household_structure)

    def make_household_without_household_log_entry(self, survey=None):
        if survey:
            if survey not in site_surveys.current_surveys:
                raise TestMixinError(
                    'Invalid survey specified. Got {}. See {} '
                    'Expected one of {}'.format(
                        survey.field_name, [s.field_name for s in site_surveys.current_surveys],
                        self.__class__.__name__))
        survey = survey or site_surveys.current_surveys[0]
        plot = self.make_confirmed_plot(household_count=1)
        household_structure = HouseholdStructure.objects.get(household__plot=plot, survey=survey.field_name)
        return household_structure

    def make_household_with_household_log_entry(self, household_status=None, survey=None):
        household_structure = self.make_household_without_household_log_entry(survey=survey)
        household_status = household_status or ELIGIBLE_REPRESENTATIVE_PRESENT
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        report_datetime = self.get_utcnow()
        self.make_household_log_entry(
            report_datetime=report_datetime,
            household_log=household_log,
            household_status=household_status)
        household_structure = HouseholdStructure.objects.get(id=household_structure.id)
        return household_structure.householdlog.householdlogentry_set.all().order_by('report_datetime')

    def make_household_with_max_enumeration_attempts(
            self, household_log=None, household_status=None, survey=None):
        """Returns household_structure after adding three unsuccessful enumeration attempts,
        or as many as are still needed."""
        household_status = household_status or ELIGIBLE_REPRESENTATIVE_ABSENT
        household_log_entrys = None
        if household_log:
            household_log_entrys = HouseholdLogEntry.objects.filter(household_log=household_log)
        if not household_log_entrys:
            household_log_entrys = self.make_household_with_household_log_entry(
                household_status=household_status, survey=survey)
        household_log = household_log_entrys[0].household_log
        household_structure = HouseholdStructure.objects.get(
            pk=household_log.household_structure.pk)
        self.assertEqual(household_structure.enumeration_attempts, 1)
        for n in range(0, 3):
            report_datetime = self.get_utcnow() + relativedelta(hours=n + 1)
            with transaction.atomic():
                try:
                    self.make_household_log_entry(
                        report_datetime=report_datetime,
                        household_log=household_log,
                        household_status=household_status)
                except EnumerationAttemptsExceeded:
                    break  # wont hit this unless app_config.max_household_log_entries > 0
                except IntegrityError:
                    pass  # maybe already added some entries somewhere else
        household_structure = HouseholdStructure.objects.get(
            pk=household_log.household_structure.pk)
        self.assertGreaterEqual(household_structure.enumeration_attempts, 3)
        self.assertGreaterEqual(HouseholdLogEntry.objects.filter(household_log=household_log).count(), 3)
        return household_structure

    def make_household_failed_enumeration_with_household_assessment(
            self, household_status=None, eligibles_last_seen_home=None, survey=None):
        household_status = household_status or NO_HOUSEHOLD_INFORMANT
        eligibles_last_seen_home = eligibles_last_seen_home or UNKNOWN_OCCUPIED
        household_structure = self.make_household_with_max_enumeration_attempts(
            household_status=household_status, survey=survey)
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

    def make_household_ready_for_enumeration(self, survey=None):
        household_structure = self.make_household_with_max_enumeration_attempts(
            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT, survey=survey)
        household_structure = HouseholdStructure.objects.get(
            pk=household_structure.pk)
        return household_structure
