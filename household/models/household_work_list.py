from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_base.model.validators.date import datetime_not_future
from edc_base.utils import get_utcnow

from ..choices import HOUSEHOLD_LOG_STATUS

from .household_structure import HouseholdStructure
from ..managers import HouseholdWorkListManager


class HouseholdWorkList(BaseUuidModel):

    """A system model that links a household to its household members
    for a given survey year and helps track the enrollment status, enumeration
    status, enumeration attempts and other system values. """

    household_structure = models.ForeignKey(HouseholdStructure, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=get_utcnow,
        validators=[datetime_not_future])

    label = models.CharField(
        max_length=25,
        help_text="label to group, e.g. T1 prep"
    )

    visit_date = models.DateField(
        editable=False)

    status = models.CharField(
        max_length=25,
        choices=(
            ('scheduled', 'Scheduled'),
            ('missed_scheduled', 'Scheduled!!'),
            ('unscheduled', 'Unscheduled'),
            ('incomplete', 'Incomplete'),
            ('done', 'Done'),
        ),
        editable=False
    )

    appt_count = models.IntegerField(
        default=0,
        editable=False,
        help_text='Number of currently scheduled appointments, including missed.'
    )

    enrolled_type = models.CharField(
        choices=(
            ('hic', 'HIC/BHS'),
            ('bhs', 'BHS Only')
        ),
        max_length=3,
        editable=False
    )

    note = models.CharField("Note", max_length=250, blank=True)

    log_date = models.DateField(
        editable=False,
        null=True,
        help_text='From household_log entries')

    log_status = models.CharField(
        verbose_name='Household Status',
        max_length=50,
        choices=HOUSEHOLD_LOG_STATUS,
        null=True,
        blank=False)

    log_attempts = models.IntegerField(default=0)

    members = models.IntegerField(default=0)

    bhs = models.IntegerField(default=0)

    hic = models.IntegerField(default=0)

    objects = HouseholdWorkListManager()

    history = HistoricalRecords()

    def __str__(self):
        return str(self.household_structure)

    def natural_key(self):
        return (self.household_structure, self.label,)
    natural_key.dependencies = ['household.householdstructure']

    class Meta:
        app_label = 'household'
        unique_together = ('household_structure', 'label')
