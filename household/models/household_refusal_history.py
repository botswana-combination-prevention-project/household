from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords

from .model_mixins import HouseholdRefusalMixin
from ..managers import HouseholdRefusalHistoryManager


class HouseholdRefusalHistory(HouseholdRefusalMixin, BaseUuidModel):
    """A system model to keep a history of deleted household refusal instances."""

    transaction = models.UUIDField()

    objects = HouseholdRefusalHistoryManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.household_structure, self.transaction, )
    natural_key.dependencies = ['household.household_structure']

    class Meta:
        app_label = 'household'
        ordering = ['household_structure', ]
