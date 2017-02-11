from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView as BaseListboardView
from edc_dashboard.forms import SearchForm as BaseSearchForm

from survey import SurveyViewMixin

from ..models.household_structure import HouseholdStructure
from .wrappers import HouseholdStructureWithLogEntryWrapper


class SearchForm(BaseSearchForm):
    action_url_name = django_apps.get_app_config(
        'household').listboard_url_name


class ListboardView(SurveyViewMixin, EdcBaseViewMixin, AppConfigViewMixin,
                    BaseListboardView):

    app_config_name = 'household'
    navbar_item_selected = 'household'
    model = HouseholdStructure
    model_wrapper_class = HouseholdStructureWithLogEntryWrapper
    search_form_class = SearchForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        plot_identifier = kwargs.get('plot_identifier')
        if plot_identifier:
            options.update(
                {'household__plot__plot_identifier': plot_identifier})
        household_identifier = kwargs.get('household_identifier')
        if household_identifier:
            options.update(
                {'household__household_identifier': household_identifier})
        return options

    def get_queryset_exclude_options(self, request, *args, **kwargs):
        options = super().get_queryset_exclude_options(
            request, *args, **kwargs)
        plot_identifier = django_apps.get_app_config(
            'plot').anonymous_plot_identifier
        options.update({'household__plot__plot_identifier': plot_identifier})
        return options
