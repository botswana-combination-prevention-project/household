from model_mommy import mommy

from edc_base.test_mixins import AddVisitMixin, ReferenceDateMixin, CompleteCrfsMixin, LoadListDataMixin

# from bcpp_member.list_data import list_data
from plot.test_mixins import PlotMixin
from household.models.household_log import HouseholdLog


class HouseholdTestMixin(PlotMixin, LoadListDataMixin):

    list_data = None  # list_data


class HouseholdMixin(ReferenceDateMixin, HouseholdTestMixin):

    def setUp(self):
        super(HouseholdMixin, self).setUp()
        self.study_site = '40'

    def make_household_log_entry(self, household_log, **options):
        return mommy.make_recipe(
            'household.householdlogentry',
            household_log=household_log,
            **options)

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
