from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_base.model.validators.date import datetime_not_future
from edc_base.utils import get_utcnow

from ..choices import HOUSEHOLD_LOG_STATUS

from .household_structure import HouseholdStructure


class HouseholdLog(BaseUuidModel):
    """A system model that links the household log to the household."""

    household_structure = models.OneToOneField(HouseholdStructure, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=get_utcnow,
        validators=[datetime_not_future])

    last_log_status = models.CharField(
        max_length=50,
        choices=HOUSEHOLD_LOG_STATUS,
        null=True,
        editable=False,
        help_text='')

    last_log_datetime = models.DateTimeField(
        null=True,
        editable=False)

    # objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return str(self.household_structure)

    def natural_key(self):
        return self.household_structure.natural_key()
    natural_key.dependencies = ['household.household_structure', ]

    class Meta:
        app_label = 'household'
