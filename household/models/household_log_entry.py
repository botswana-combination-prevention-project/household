from django.apps import apps as django_apps
from django.db import models
from django_crypto_fields.fields import EncryptedTextField

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_base.model.validators import datetime_not_future
from edc_base.utils import get_utcnow

from survey import site_surveys

from ..choices import NEXT_APPOINTMENT_SOURCE, HOUSEHOLD_LOG_STATUS
from ..exceptions import HouseholdLogError, EnumerationAttemptsExceeded
from ..managers import LogEntryManager

from .household_log import HouseholdLog


class HouseholdLogEntry(BaseUuidModel):
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

    def common_clean(self):
        # only allow log entry for current surveys and mapper.map_area.
        app_config = django_apps.get_app_config('household')

        if not self.id:
            if not self.household_log.household_structure.survey_schedule_object.current:
                raise HouseholdLogError(
                    '{} may only be created for the current survey. Got {}.'.format(
                        self._meta.verbose_name,
                        self.household_log.household_structure.survey_schedule_object.field_value))

            # only allow x instances, set in app_config, set to zero to bypass
            if app_config.max_household_log_entries:
                count = self.__class__.objects.filter(household_log=self.household_log).count()
                if count >= app_config.max_household_log_entries:
                    raise EnumerationAttemptsExceeded(
                        'Maximum number of enumeration attempts already met. {} is not '
                        'required. Got {}.'.format(self._meta.verbose_name, count))
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        common_clean_exceptions = super().common_clean_exceptions()
        common_clean_exceptions.extend([HouseholdLogError, EnumerationAttemptsExceeded])
        return common_clean_exceptions

    def natural_key(self):
        return (self.report_datetime, ) + self.household_log.natural_key()
    natural_key.dependencies = ['household.household_log']

    def __str__(self):
        return '{} on {}'.format(
            self.household_status, self.report_datetime.strftime('%Y-%m-%d %H:%M%Z'))

    class Meta:
        app_label = 'household'
        unique_together = ('household_log', 'report_datetime')
        ordering = ('report_datetime', )
