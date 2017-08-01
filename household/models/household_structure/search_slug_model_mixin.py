from edc_search.model_mixins import SearchSlugModelMixin as BaseSearchSlugModelMixin


class SearchSlugModelMixin(BaseSearchSlugModelMixin):

    def get_slugs(self):
        slugs = super().get_slugs()
        return slugs + self.household.get_slugs()

    class Meta:
        abstract = True
