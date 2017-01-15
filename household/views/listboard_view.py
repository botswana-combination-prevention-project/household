from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardViewMixin

from survey import SurveyViewMixin

from .listboard_mixins import HouseholdFilteredListViewMixin, HouseholdSearchViewMixin, HouseholdAppConfigViewMixin


class ListBoardView(EdcBaseViewMixin, ListboardViewMixin, HouseholdAppConfigViewMixin,
                    HouseholdFilteredListViewMixin, HouseholdSearchViewMixin,
                    SurveyViewMixin, TemplateView, FormView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
