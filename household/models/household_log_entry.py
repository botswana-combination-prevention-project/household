from django.db import models
from django_crypto_fields.fields import EncryptedTextField

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_base.model.validators import datetime_not_future

from ..choices import NEXT_APPOINTMENT_SOURCE, HOUSEHOLD_LOG_STATUS

from .household_log import HouseholdLog


class HouseholdLogEntry(BaseUuidModel):
    """A model completed by the user each time the household is visited."""
    household_log = models.ForeignKey(HouseholdLog)

    report_datetime = models.DateField(
        verbose_name="Report date",
        validators=[datetime_not_future])

    household_status = models.CharField(
        verbose_name='Household Status',
        max_length=50,
        choices=HOUSEHOLD_LOG_STATUS,
        null=True,
        blank=False)

    next_appt_datetime = models.DateTimeField(
        verbose_name="Re-Visit On",
        help_text="The date and time to revisit household",
        null=True,
        blank=True)

    next_appt_datetime_source = models.CharField(
        verbose_name="Source",
        max_length=25,
        choices=NEXT_APPOINTMENT_SOURCE,
        help_text='source of information for the appointment date',
        null=True,
        blank=True)

    comment = EncryptedTextField(
        null=True,
        blank=True)

    # objects = LogEntryManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.report_datetime, ) + self.household_log.natural_key()
    natural_key.dependencies = ['household.household_log', ]

    def __str__(self):
        household_log = self.household_log or None
        return '{} ({})'.format(household_log, self.report_datetime.strftime('%Y-%m-%d'))

    class Meta:
        app_label = 'household'
        unique_together = ('household_log', 'report_datetime')
