from django.db import models
from django_crypto_fields.fields import EncryptedTextField

from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_validators import datetime_not_future, datetime_is_future
from edc_base.utils import get_utcnow

from survey.model_mixins import SurveyScheduleModelMixin

from ..choices import NEXT_APPOINTMENT_SOURCE, HOUSEHOLD_LOG_STATUS
from ..managers import LogEntryManager

from .household_log import HouseholdLog


class HouseholdLogEntry(SurveyScheduleModelMixin, BaseUuidModel):
    """A model completed by the user each time the household is visited."""

    household_log = models.ForeignKey(HouseholdLog, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=get_utcnow,
        validators=[datetime_not_future])

    household_status = models.CharField(
        verbose_name='Household Status',
        max_length=50,
        choices=HOUSEHOLD_LOG_STATUS,
        null=True,
        blank=False)

    next_appt_datetime = models.DateTimeField(
        verbose_name="[RA]: When may we visit again?",
        help_text="The date and time to visit household again.",
        validators=[datetime_is_future],
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

    objects = LogEntryManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.survey_schedule = self.household_log.household_structure.survey_schedule_object.field_value
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.report_datetime, ) + self.household_log.natural_key()
    natural_key.dependencies = ['household.household_log']

    def __str__(self):
        return '{} on {}'.format(
            self.household_status, self.report_datetime.strftime('%Y-%m-%d %H:%M%Z'))

    class Meta:
        unique_together = ('household_log', 'report_datetime')
        ordering = ('report_datetime', )
