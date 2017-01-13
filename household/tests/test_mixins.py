from model_mommy import mommy

from edc_base_test.mixins import LoadListDataMixin
from edc_base_test.exceptions import TestMixinError

from plot.tests import PlotMixin
from survey.test_mixins import SurveyTestMixin

from ..constants import (
    ELIGIBLE_REPRESENTATIVE_PRESENT, NO_HOUSEHOLD_INFORMANT,
    UNKNOWN_OCCUPIED)
from ..models import HouseholdStructure, is_no_informant
from ..models.utils import is_failed_enumeration_attempt_household_status
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from survey.site_surveys import site_surveys


class HouseholdTestMixin(PlotMixin, LoadListDataMixin):

    list_data = None  # list_data


class HouseholdMixin(SurveyTestMixin, HouseholdTestMixin):

    def setUp(self):
        super().setUp()
        self.study_site = '40'
        self.household_structures = None

    def _make_plot(self, household_count=None, **options):
        """Returns a new plot with x households created.

        For internal use."""
        plot = self.make_confirmed_plot(household_count=household_count or 1)
        return plot

    def _add_attempts(self, household_structure, survey_schedule=None, attempts=None, **options):
        """Returns None after adding as many enumerations attempts as specified.

        For internal use."""
        if options.get('household_status'):
            attempts = attempts or 1
        else:
            attempts = attempts or 0
            options.update(household_status=ELIGIBLE_REPRESENTATIVE_PRESENT)
        for _ in range(0, attempts):
            self.add_enumeration_attempt(
                household_structure=household_structure,
                **options)

    def make_household_structure(
            self, survey_schedule=None, attempts=None, **options):
        """Returns a household_structure instance by making a new plot with
        households.

        * attempts: add HouseholdLogEntry x <attempts>. Default: 0
        * survey_schedule: Default: first current survey_schedule

        Adds as many HouseholdLogEntry instances as `attempts` to the Household
        of the given survey_schedule.
        """
        plot = self._make_plot(**options)
        survey_schedule = survey_schedule or self.get_survey_schedule(0)
#         if survey_schedule not in site_surveys.get_survey_schedules(
#                 group_name=survey_schedule.group_name, current=True):
#             raise TestMixinError(
#                 'System only makes household_structure for current survey schedules.')
        for household in plot.household_set.all():
            try:
                household_structure = HouseholdStructure.objects.get(
                    household=household,
                    survey_schedule=survey_schedule.field_value)
            except HouseholdStructure.DoesNotExist:
                pass
            else:
                # if attempts > 0 add them now
                self._add_attempts(
                    household_structure,
                    survey_schedule=survey_schedule,
                    attempts=attempts, **options)

        # requery
        household_structure = HouseholdStructure.objects.get(
            household__plot=plot,
            survey_schedule=survey_schedule.field_value)

        return household_structure

    def add_enumeration_attempt(self, household_structure, household_status=None, **options):
        """Returns household_structure after a household log or "enumeration attempt",

            * household_status: (default: ELIGIBLE_REPRESENTATIVE_PRESENT)
        """

        household_status = household_status or ELIGIBLE_REPRESENTATIVE_PRESENT

        last = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last()
        if last:
            default_report_datetime = last.report_datetime + relativedelta(hours=1)
        else:
            default_report_datetime = self.get_utcnow()
        report_datetime = options.get('report_datetime', default_report_datetime)

        mommy.make_recipe(
            'household.householdlogentry',
            report_datetime=report_datetime,
            household_log=household_structure.householdlog,
            household_status=household_status)

        household_structure = HouseholdStructure.objects.get(id=household_structure.id)
        self.assertGreater(household_structure.enumeration_attempts, 0)
        self.assertGreater(
            household_structure.householdlog.householdlogentry_set.all().count(), 0)
        return household_structure

    def add_failed_enumeration_attempt(self, household_structure, household_status=None, **options):
        """Adds a failed enumermation attempt."""
        household_status = household_status or NO_HOUSEHOLD_INFORMANT
        if not is_failed_enumeration_attempt_household_status(household_status):
            raise TestMixinError(
                'Expected a household status for a failed enumeration '
                'attempt. Got {}'.format(household_status))
        return self.add_enumeration_attempt(
            household_structure=household_structure,
            household_status=household_status, **options)

    def fail_enumeration(
            self, household_structure, household_status=None,
            eligibles_last_seen_home=None, **options):
        """Adds three failed enumeration attempts and the household assemssment."""
        household_status = household_status or NO_HOUSEHOLD_INFORMANT
        eligibles_last_seen_home = eligibles_last_seen_home or UNKNOWN_OCCUPIED

        report_datetime = options.get('report_datetime', self.get_utcnow())

        # create three failed attempts as is required by
        # household_assessment validation
        for i in range(0, 3):
            household_structure = self.add_failed_enumeration_attempt(
                household_structure,
                household_status=household_status,
                report_datetime=self.get_utcnow() + relativedelta(hours=i),
                **options)

        household_assessment = mommy.make_recipe(
            'household.householdassessment',
            report_datetime=report_datetime,
            household_structure=household_structure,
            eligibles_last_seen_home=eligibles_last_seen_home)

        self.assertEqual(
            household_structure.no_informant,
            is_no_informant(household_assessment))
        return household_structure

    def add_enumeration_attempt2(self, household_structure, household_status=None, **options):
        """Like add_enumeration_attempt but returns a household log entry.

        If household status is a failed attempt will call `add_failed_enumeration_attempt`
        otherwise calls `add_enumeration_attempt`."""

        if is_failed_enumeration_attempt_household_status(household_status):
            household_structure = self.add_failed_enumeration_attempt(
                household_structure=household_structure,
                household_status=household_status,
                **options)
        else:
            household_structure = self.add_enumeration_attempt(
                household_structure=household_structure,
                household_status=household_status,
                **options)
        return household_structure.householdlog.householdlogentry_set.order_by('created').last()

    def make_household_refusal(self, household_log_entry=None, household_structure=None):
        if household_log_entry:
            household_structure = household_log_entry.household_log.household_structure
        mommy.make_recipe(
            'household.householdrefusal',
            report_datetime=self.get_utcnow(),
            household_structure=household_structure)
