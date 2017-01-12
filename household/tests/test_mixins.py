from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from django.db import transaction
from django.db.utils import IntegrityError

from edc_base_test.mixins import LoadListDataMixin

from plot.tests import PlotMixin
from survey import site_surveys

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

    def is_survey_schedule(self, survey_schedule):
        """Verifies the survey schedule object is valid.

        Does not have to be a current survey schedule."""
        if survey_schedule:
            survey_schedule = site_surveys.get_survey_schedule_from_field_value(
                survey_schedule.field_value)
            if not survey_schedule:
                raise TestMixinError(
                    'Invalid survey specified. Got {}. See TestCase {} '
                    'Expected one of {}'.format(
                        survey_schedule.field_value,
                        self.__class__.__name__,
                        [s.field_value for s in site_surveys.get_survey_schedules()]))
        return survey_schedule

    def get_survey_schedule(self, name=None, index=None, field_value=None,
                            group_name=None, current=None):
        """Returns a survey schedule object.

        You can also just use site_surveys!

            * name: survey schedule name, e.g. 'bcpp_year.example-year-1'
            * field_value: survey schedule field_value, e.g. 'bcpp_year.example-year-1.test_community'
            * group_name: survey schedule group_name, e.g. 'bcpp_year'.
            * index: list index of the ordered list of survey schedules
            * current: if current=True only return a survey schedule if it is a current.
                       If group_name is None, current defaults to True"""
        if name:
            survey_schedule = site_surveys.get_survey_schedule(name=name)
            if current:
                survey_schedule = survey_schedule if survey_schedule.current else None
        else:
            current = current if group_name else True
            survey_schedules = site_surveys.get_survey_schedules(
                group_name=group_name, current=current)
            survey_schedule = survey_schedules[index or 0]
        return survey_schedule

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

    def make_household_without_household_log_entry(self, survey_schedule=None):
        # note: accepts a survey schedule object not string

        if not self.is_survey_schedule(survey_schedule):
            survey_schedule = site_surveys.get_survey_schedules(current=True)[0]

        plot = self.make_confirmed_plot(household_count=1)
        household_structure = HouseholdStructure.objects.get(
            household__plot=plot, survey_schedule=survey_schedule.field_value)
        return household_structure

    def make_household_with_household_log_entry(self, household_status=None, survey_schedule=None):

        if not self.is_survey_schedule(survey_schedule):
            survey_schedule = site_surveys.get_survey_schedules(current=True)[0]

        household_structure = self.make_household_without_household_log_entry(
            survey_schedule=survey_schedule)
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
            self, household_log=None, household_status=None, survey_schedule=None):
        """Returns household_structure after adding three unsuccessful enumeration attempts,
        or as many as are still needed."""
        household_status = household_status or ELIGIBLE_REPRESENTATIVE_ABSENT
        household_log_entrys = None
        if household_log:
            household_log_entrys = HouseholdLogEntry.objects.filter(household_log=household_log)
        if not household_log_entrys:
            household_log_entrys = self.make_household_with_household_log_entry(
                household_status=household_status,
                survey_schedule=survey_schedule)
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
            self, household_status=None, eligibles_last_seen_home=None, survey_schedule=None):
        household_status = household_status or NO_HOUSEHOLD_INFORMANT
        eligibles_last_seen_home = eligibles_last_seen_home or UNKNOWN_OCCUPIED
        household_structure = self.make_household_with_max_enumeration_attempts(
            household_status=household_status,
            survey_schedule=survey_schedule)
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

    def make_household_ready_for_enumeration(self, survey_schedule=None):
        household_structure = self.make_household_with_max_enumeration_attempts(
            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT,
            survey_schedule=survey_schedule)
        household_structure = HouseholdStructure.objects.get(
            pk=household_structure.pk)
        return household_structure
