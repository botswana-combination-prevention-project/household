from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardViewMixin, AppConfigViewMixin

from survey import SurveyViewMixin

from .listboard_mixins import FilteredListViewMixin, SearchViewMixin


class ListBoardView(FilteredListViewMixin, SearchViewMixin, ListboardViewMixin,
                    SurveyViewMixin, EdcBaseViewMixin, AppConfigViewMixin,
                    TemplateView, FormView):

    app_config_name = 'household'
    navbar_item_selected = 'household'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def filtered_queryset(self):
        qs = super().filtered_queryset
        if qs:
            plot_identifier = django_apps.get_app_config(
                'plot').anonymous_plot_identifier
            return qs.exclude(
                household__plot__plot_identifier=plot_identifier).order_by(
                    self.filtered_queryset_ordering)
        return qs

    def search_queryset(self, search_term, **kwargs):
        qs = super().search_queryset(search_term, **kwargs)
        if qs:
            plot_identifier = django_apps.get_app_config(
                'plot').anonymous_plot_identifier
            return qs.exclude(
                household__plot__plot_identifier=plot_identifier).order_by(
                    self.filtered_queryset_ordering)
        return qs
