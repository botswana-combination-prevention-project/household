from django.apps import apps as django_apps
from django.db.models import Q

from edc_dashboard.view_mixins import FilteredListViewMixin
from edc_search.view_mixins import SearchViewMixin

from plot.views import PlotAppConfigViewMixin

from ..models import HouseholdStructure

from .wrappers import HouseholdStructureWithLogEntryWrapper


class HouseholdAppConfigViewMixin(PlotAppConfigViewMixin):

    app_config_name = 'household'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            enumeration_listboard_url_name=django_apps.get_app_config('enumeration').listboard_url_name,
            member_listboard_url_name=django_apps.get_app_config('member').listboard_url_name,
        )
        return context


class HouseholdSearchViewMixin(SearchViewMixin):

    search_model = HouseholdStructure
    search_model_wrapper_class = HouseholdStructureWithLogEntryWrapper
    search_queryset_ordering = '-modified'

    def search_options(self, search_term, **kwargs):
        q, options = super().search_options(search_term, **kwargs)
        q = q | (
            Q(household__household_identifier__icontains=search_term) |
            Q(household__plot__plot_identifier__icontains=search_term) |
            Q(household__id__iexact=search_term))
        return q, options


class HouseholdFilteredListViewMixin(FilteredListViewMixin):

    filter_model = HouseholdStructure
    filtered_model_wrapper_class = HouseholdStructureWithLogEntryWrapper
    filtered_queryset_ordering = '-modified'
    url_lookup_parameters = [
        'id',
        ('household_identifier', 'household__household_identifier'),
        ('plot_identifier', 'household__plot__plot_identifier')]
