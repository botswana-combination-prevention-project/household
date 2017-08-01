from uuid import uuid4

from django.db import models

from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel

from ..managers import HouseholdRefusalHistoryManager

from .model_mixins import HouseholdRefusalMixin


class HouseholdRefusalHistory(HouseholdRefusalMixin, BaseUuidModel):
    """A system model to keep a history of deleted household refusal instances."""

    transaction = models.UUIDField(default=uuid4)

    objects = HouseholdRefusalHistoryManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.transaction,) + self.household_structure.natural_key()
    natural_key.dependencies = ['household.household_structure']

    class Meta:
        ordering = ['household_structure', ]
