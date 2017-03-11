from django.db import models

from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_validators import datetime_not_future
from edc_base.utils import get_utcnow

from .household_structure import HouseholdStructure

from ..managers import HouseholdLogManager


class HouseholdLog(BaseUuidModel):
    """A system model that links the household log to the household."""

    household_structure = models.OneToOneField(
        HouseholdStructure, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=get_utcnow,
        validators=[datetime_not_future])

    objects = HouseholdLogManager()

    history = HistoricalRecords()

    def __str__(self):
        return str(self.household_structure)

    def natural_key(self):
        return self.household_structure.natural_key()
    natural_key.dependencies = ['household.household_structure']

    @property
    def last_log_status(self):
        try:
            return self.householdlogentry_set.all().order_by('report_datetime').last().household_status
        except AttributeError:
            return None

    @property
    def last_log_datetime(self):
        try:
            return self.householdlogentry_set.all().order_by('report_datetime').last().report_datetime
        except AttributeError:
            return None

    class Meta:
        app_label = 'household'
