from uuid import uuid4

from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords

from .model_mixins import HouseholdRefusalMixin


class HouseholdRefusalHistory(HouseholdRefusalMixin, BaseUuidModel):
    """A system model to keep a history of deleted household refusal instances."""

    transaction = models.UUIDField(default=uuid4)

    # objects = HistoryManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.transaction, )

    class Meta:
        app_label = 'household'
        ordering = ['household_structure', ]
