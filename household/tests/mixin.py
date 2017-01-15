from edc_base_test.mixins.load_list_data_mixin import LoadListDataMixin
from edc_base_test.mixins.dates_test_mixin import DatesTestMixin

from plot.tests import PlotTestMixin
from survey.tests import SurveyTestMixin

from .household_test_mixin import HouseholdTestMixin


class HouseholdMixin(PlotTestMixin, LoadListDataMixin, SurveyTestMixin, DatesTestMixin, HouseholdTestMixin):

    list_data = None  # list_data
