from edc_search.model_mixins import SearchSlugModelMixin as BaseSearchSlugModelMixin


class SearchSlugModelMixin(BaseSearchSlugModelMixin):

    def get_search_slug_fields(self):
        return [
            'household.household_identifier',
            'household.plot.plot_identifier',
            'household.plot.map_area']

    class Meta:
        abstract = True
