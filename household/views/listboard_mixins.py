from django.db.models import Q

from edc_dashboard.view_mixins import FilteredListViewMixin as BaseFilteredListViewMixin
from edc_search.view_mixins import SearchViewMixin as BaseSearchViewMixin

from ..models import HouseholdStructure

from .wrappers import HouseholdStructureWithLogEntryWrapper


class SearchViewMixin(BaseSearchViewMixin):

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


class FilteredListViewMixin(BaseFilteredListViewMixin):

    filter_model = HouseholdStructure
    filtered_model_wrapper_class = HouseholdStructureWithLogEntryWrapper
    filtered_queryset_ordering = '-modified'
    url_lookup_parameters = [
        ('id', 'id'),
        ('household_identifier', 'household__household_identifier'),
        ('plot_identifier', 'household__plot__plot_identifier')]
