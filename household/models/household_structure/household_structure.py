from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_base.utils import get_utcnow
from edc_base.model.validators.date import datetime_not_future

from survey.model_mixins import SurveyScheduleModelMixin

from ...managers import HouseholdStructureManager

from ..household import Household

from .enrollment_model_mixin import EnrollmentModelMixin
from .enumeration_model_mixin import EnumerationModelMixin


class HouseholdStructure(EnrollmentModelMixin, EnumerationModelMixin,
                         SurveyScheduleModelMixin, BaseUuidModel):

    """A system model that links a household to its household members
    for a given survey year and helps track the enrollment status, enumeration
    status, enumeration attempts and other system values. """

    household = models.ForeignKey(Household, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=get_utcnow,
        validators=[datetime_not_future])

    progress = models.CharField(
        verbose_name='Progress',
        max_length=25,
        default='Not Started',
        null=True,
        editable=False)

    note = models.CharField("Note", max_length=250, blank=True)

    objects = HouseholdStructureManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.survey_schedule,) + self.household.natural_key()
    natural_key.dependencies = ['household.household']

    def __str__(self):
        return '{} for {}'.format(self.household, self.survey_schedule)

    def save(self, *args, **kwargs):
        if not self.id:
            # household creates household_structure, so use household.report_datetime.
            self.report_datetime = self.household.report_datetime
        super().save(*args, **kwargs)

    @property
    def next(self):
        """Returns the next household structure instance or None in the survey_schedule sequence."""
        return self.household.householdstructure_set.filter(
            survey_schedule=self.survey_schedule_object.next.field_value).first()

    class Meta:
        app_label = 'household'
        unique_together = ('household', 'survey_schedule')
        ordering = ('household', 'survey_schedule')
