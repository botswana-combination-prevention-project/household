from django.db.models.constants import LOOKUP_SEP


class HouseholdQuerysetViewMixin:

    household_queryset_lookups = []

    @property
    def household_lookup_prefix(self):
        household_lookup_prefix = LOOKUP_SEP.join(
            self.household_queryset_lookups)
        return '{}__'.format(household_lookup_prefix) if household_lookup_prefix else ''

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get('household_identifier'):
            options.update(
                {'{}household_identifier'.format(self.household_lookup_prefix):
                 kwargs.get('household_identifier')})
        return options
