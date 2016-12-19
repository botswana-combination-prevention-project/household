from edc_base.model.models import HistoricalRecords, BaseUuidModel

from .model_mixins import HouseholdRefusalMixin
from ..managers import HouseholdRefusalManager


class HouseholdRefusal(HouseholdRefusalMixin, BaseUuidModel):
    """A model completed by the user to indicate the reason why a household
    cannot be enumerated."""

    objects = HouseholdRefusalManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.household_structure,)
    natural_key.dependencies = ['household.household_structure']

    class Meta:
        app_label = 'household'
        ordering = ['household_structure', ]
