from model_mommy import mommy

from edc_base.test_mixins import AddVisitMixin, ReferenceDateMixin, CompleteCrfsMixin, LoadListDataMixin

# from bcpp_member.list_data import list_data
from plot.test_mixins import PlotMixin
from household.models.household_log import HouseholdLog
from household.models.household_structure import HouseholdStructure
from household.constants import ELIGIBLE_REPRESENTATIVE_PRESENT
from survey.site_surveys import site_surveys
from household.models.household_log_entry import HouseholdLogEntry


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

    def make_household_with_log_entry(self, household_status=None, survey_name=None):
        household_status = household_status or ELIGIBLE_REPRESENTATIVE_PRESENT
        survey_name = survey_name or 'example-survey'
        surveys = [survey for survey in site_surveys.surveys if survey_name in survey.survey_schedule]
        plot = self.make_confirmed_plot(household_count=1)
        household_structures = HouseholdStructure.objects.filter(household__plot=plot, survey__in=surveys)
        for household_structure in household_structures:
            household_log = HouseholdLog.objects.get(household_structure=household_structure)
            self.make_household_log_entry(household_log=household_log, household_status=household_status)
        return HouseholdLogEntry.objects.filter(household_log__household_structure=household_structure)

    def make_household_refusal(self, household_log_entry=None, household_structure=None):
        if household_log_entry:
            household_structure = household_log_entry.household_log.household_structure
        mommy.make_recipe(
            'household.householdrefusal',
            household_structure=household_structure)

    def make_enumerated_household(self, **options):
        member_count = options.get('member_count', 5)
        options.update(member_count=member_count)

    def make_member(self):
        pass

    def make_minor_member(self):
        pass

    def make_senior_member(self):
        pass

    def make_head_of_household(self):
        pass
