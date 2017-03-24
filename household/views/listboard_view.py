from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView as BaseListboardView

from plot.view_mixins import PlotQuerysetViewMixin
from survey import SurveyViewMixin

from ..models.household_structure import HouseholdStructure
from ..view_mixins import HouseholdQuerysetViewMixin, HouseholdStructureWithLogEntryWrapper


class ListboardView(SurveyViewMixin, EdcBaseViewMixin, AppConfigViewMixin,
                    HouseholdQuerysetViewMixin, PlotQuerysetViewMixin,
                    BaseListboardView):

    app_config_name = 'household'
    navbar_item_selected = 'household'
    model = HouseholdStructure
    model_wrapper_class = HouseholdStructureWithLogEntryWrapper

    plot_queryset_lookups = ['household', 'plot']
    household_queryset_lookups = ['household']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
