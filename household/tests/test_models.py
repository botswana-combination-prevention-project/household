from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_map.site_mappers import site_mappers
from plot.models import Plot
from survey.site_surveys import site_surveys

from ..constants import NO_HOUSEHOLD_INFORMANT, ELIGIBLE_REPRESENTATIVE_ABSENT
from ..constants import REFUSED_ENUMERATION
from ..exceptions import HouseholdAssessmentError
from ..models import Household, HouseholdLogEntry, HouseholdRefusal
from ..models import HouseholdStructure
from .household_test_helper import HouseholdTestHelper, get_utcnow
from .mappers import TestMapper


@tag('models')
class TestHousehold(TestCase):

    household_helper = HouseholdTestHelper()

    def setUp(self):
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)

    def test_household_str(self):
        plot = self.household_helper.make_confirmed_plot(household_count=1)
        household = plot.household_set.all()[0]
        self.assertTrue(str(household))

    def test_household_structure_str(self):
        plot = self.household_helper.make_confirmed_plot(household_count=1)
        household = plot.household_set.all()[0]
        household_structure = household.householdstructure_set.all()[0]
        self.assertTrue(str(household_structure))

    def test_creates_household_structure(self):
        """Asserts household structure instances are created
        when households are created.
        """
        plot = self.household_helper.make_confirmed_plot(household_count=3)
        survey_count = len(site_surveys.get_survey_schedules(current=True))
        self.assertGreater(survey_count, 0)
        self.assertEqual(HouseholdStructure.objects.filter(
            household__plot=plot).count(), survey_count * 3)

    def test_deletes_household_structure(self):
        """Asserts deletes household structure instances households
        are deleted.
        """
        plot = self.household_helper.make_confirmed_plot(household_count=3)
        survey_count = len(site_surveys.get_survey_schedules(current=True))
        self.assertGreater(survey_count, 0)

        # created 3 households as expected
        self.assertEqual(Household.objects.filter(plot=plot).count(), 3)

        for household in Household.objects.filter(plot=plot):
            self.assertEqual(HouseholdStructure.objects.filter(
                household=household).count(), survey_count)

        plot.household_count = 1
        plot.save()

        #  deleted two of the three households
        self.assertEqual(Household.objects.filter(plot=plot).count(), 1)

        for household in Household.objects.filter(plot=plot):
            self.assertEqual(HouseholdStructure.objects.filter(
                household=household).count(), survey_count)

    def test_cannot_delete_household_with_household_log_entry(self):
        """Asserts PROTECT will prevent plot from deleting existing households
        on save."""

        household_structure = self.household_helper.make_household_structure(
            household_count=5, attempts=1)
        plot = household_structure.household.plot
        self.assertEqual(plot.household_count, 5)
        self.assertEqual(HouseholdLogEntry.objects.filter(
            household_log__household_structure__household__plot=plot).count(), 5)

        # try removing households
        plot.household_count = 1
        plot.save()

        # assert deletion failed
        plot = Plot.objects.get(pk=plot.pk)
        self.assertEqual(HouseholdLogEntry.objects.filter(
            household_log__household_structure__household__plot=plot).count(), 5)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 5)

        # assert plot value was not changed
        self.assertEqual(plot.household_count, 5)

    def test_cannot_only_delete_households_without_household_log_entry(self):
        household_structure = self.household_helper.make_household_structure(
            household_count=3, attempts=1)
        plot = household_structure.household.plot
        self.assertEqual(plot.household_count, 3)

        self.assertEqual(HouseholdLogEntry.objects.filter(
            household_log__household_structure__household__plot=plot).count(), 3)
        plot.household_count = 1
        plot.save()

        plot = Plot.objects.get(pk=plot.pk)
        self.assertEqual(HouseholdLogEntry.objects.filter(
            household_log__household_structure__household__plot=plot).count(), 3)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 3)

        # assert plot value was not changed
        self.assertEqual(plot.household_count, 3)

    def test_can_delete_household_without_household_log_entry(self):
        plot = self.household_helper.make_confirmed_plot(household_count=2)
        plot.household_count = 1
        plot.save()
        self.assertEqual(Household.objects.filter(plot=plot).count(), 1)

    def test_household_with_refused_enumeration_by_log_entry(self):
        household_structure = self.household_helper.make_household_structure()
        household_structure = self.household_helper.add_failed_enumeration_attempt(
            household_structure=household_structure,
            household_status=REFUSED_ENUMERATION)

        for household_log_entry in household_structure.householdlog.householdlogentry_set.all():
            self.assertEqual(
                household_log_entry.household_log.last_log_status, REFUSED_ENUMERATION)
            self.assertEqual(
                household_log_entry.household_log.household_structure.failed_enumeration_attempts, 1)
            self.assertFalse(
                household_log_entry.household_log.household_structure.refused_enumeration)

    def test_household_with_refused_enumeration_confirmed(self):
        household_structure = self.household_helper.make_household_structure(
            household_status=REFUSED_ENUMERATION)
        for household_log_entry in household_structure.householdlog.householdlogentry_set.all():
            self.household_helper.make_household_refusal(
                household_log_entry=household_log_entry)
            self.assertEqual(
                household_log_entry.household_log.household_structure.failed_enumeration_attempts, 1)
            self.assertTrue(
                household_log_entry.household_log.household_structure.refused_enumeration)

    def test_delete_refused_enumeration_confirmed_updates_household_structure(self):
        household_structure = self.household_helper.make_household_structure(
            household_status=REFUSED_ENUMERATION)
        for household_log_entry in household_structure.householdlog.householdlogentry_set.all():
            self.household_helper.make_household_refusal(
                household_log_entry=household_log_entry)
        HouseholdRefusal.objects.all().delete()
        household_log_entrys = HouseholdLogEntry.objects.filter(
            household_log=household_log_entry.household_log)
        for household_log_entry in household_log_entrys:
            self.assertEqual(
                household_log_entry.household_log.household_structure.failed_enumeration_attempts, 1)
            self.assertFalse(
                household_log_entry.household_log.household_structure.refused_enumeration)

    def test_household_with_no_informant(self):
        household_structure = self.household_helper.make_household_structure(
            household_status=NO_HOUSEHOLD_INFORMANT)
        for household_log_entry in household_structure.householdlog.householdlogentry_set.all():
            self.assertEqual(
                household_log_entry.household_log.last_log_status, NO_HOUSEHOLD_INFORMANT)

    def test_household_with_no_representative(self):
        household_structure = self.household_helper.make_household_structure(
            household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
        for household_log_entry in household_structure.householdlog.householdlogentry_set.all():
            self.assertEqual(
                household_log_entry.household_log.last_log_status, ELIGIBLE_REPRESENTATIVE_ABSENT)

    def test_household_log_entry_updates_household_log_last_log_status(self):

        # first log entry
        household_structure = self.household_helper.make_household_structure(
            household_status=NO_HOUSEHOLD_INFORMANT)
        for household_log_entry in household_structure.householdlog.householdlogentry_set.all():
            self.assertEqual(
                household_log_entry.household_log.last_log_status,
                NO_HOUSEHOLD_INFORMANT)

        # next log entry
        last = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last()
        household_log_entry = self.household_helper.add_enumeration_attempt2(
            household_structure,
            household_status=ELIGIBLE_REPRESENTATIVE_ABSENT,
            report_datetime=last.report_datetime + relativedelta(hours=1))
        self.assertEqual(
            household_log_entry.household_log.last_log_status,
            ELIGIBLE_REPRESENTATIVE_ABSENT)

        # next log entry
        last = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last()
        household_log_entry = self.household_helper.add_enumeration_attempt2(
            household_structure,
            household_status=ELIGIBLE_REPRESENTATIVE_ABSENT,
            report_datetime=last.report_datetime + relativedelta(hours=2))
        self.assertEqual(
            household_log_entry.household_log.last_log_status,
            ELIGIBLE_REPRESENTATIVE_ABSENT)

        # next log entry
        last = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last()
        household_log_entry = self.household_helper.add_enumeration_attempt2(
            household_structure,
            household_status=REFUSED_ENUMERATION,
            report_datetime=last.report_datetime + relativedelta(hours=2))
        self.assertEqual(
            household_log_entry.household_log.last_log_status,
            REFUSED_ENUMERATION)

    def test_household_assessment_needs_three_enumeration_attempts(self):

        household_structure = self.household_helper.make_household_structure(
            household_status=REFUSED_ENUMERATION)

        self.assertEqual(household_structure.enumeration_attempts, 1)
        self.assertEqual(household_structure.failed_enumeration_attempts, 1)

        # fail to create, needs more enumeration_attempts
        self.assertRaises(
            HouseholdAssessmentError,
            mommy.make_recipe,
            'household.householdassessment',
            household_structure=household_structure)

        household_structure = self.household_helper.add_failed_enumeration_attempt(
            household_structure=household_structure,
            household_status=REFUSED_ENUMERATION,
            report_datetime=get_utcnow() + relativedelta(hours=1))
        household_structure = self.household_helper.add_failed_enumeration_attempt(
            household_structure=household_structure,
            household_status=REFUSED_ENUMERATION,
            report_datetime=get_utcnow() + relativedelta(hours=2))

        try:
            mommy.make_recipe(
                'household.householdassessment',
                household_structure=household_structure)
        except HouseholdAssessmentError:
            self.fail('HouseholdAssessmentError unexpectedly NOT raised')

    def test_household_assessment_updates_failed_enumeration(self):
        household_structure = self.household_helper.make_household_structure()
        household_structure = self.household_helper.fail_enumeration(
            household_structure)
        self.assertTrue(household_structure.failed_enumeration)

    def test_household_assessment_updates_no_informant(self):
        household_structure = self.household_helper.make_household_structure()
        household_structure = self.household_helper.fail_enumeration(
            household_structure)
        self.assertTrue(household_structure.no_informant)

    def test_household_assessment_updates_failed_enumeration_on_delete(self):
        household_structure = self.household_helper.make_household_structure()
        for _ in range(0, 3):
            household_structure = self.household_helper.add_failed_enumeration_attempt(
                household_structure)
        household_structure = HouseholdStructure.objects.get(
            pk=household_structure.pk)
        self.assertFalse(household_structure.failed_enumeration)

    def test_household_assessment_updates_no_informant_on_delete(self):
        household_structure = self.household_helper.make_household_structure()
        for _ in range(0, 3):
            household_structure = self.household_helper.add_failed_enumeration_attempt(
                household_structure)
        household_structure = HouseholdStructure.objects.get(
            pk=household_structure.pk)
        self.assertFalse(household_structure.no_informant)
