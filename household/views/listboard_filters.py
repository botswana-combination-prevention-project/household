from edc_dashboard.listboard_filter import ListboardFilter, ListboardViewFilters


class HouseholdListboardViewFilters(ListboardViewFilters):

    all = ListboardFilter(
        name='all',
        position=0,
        label='All',
        lookup={})

    enrolled = ListboardFilter(
        label='Enrolled',
        position=5,
        lookup={'enrolled': True})

    not_enrolled = ListboardFilter(
        label='Not enrolled',
        position=6,
        lookup={'enrolled': False})
