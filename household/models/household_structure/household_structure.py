from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_base.model_managers import HistoricalRecords
from edc_search.model_mixins import SearchSlugManager

from survey.iterators import SurveyScheduleIterator
from survey.model_mixins import SurveyScheduleModelMixin

from ...managers import HouseholdStructureManager
from ..household import Household
from .enrollment_model_mixin import EnrollmentModelMixin
from .enumeration_model_mixin import EnumerationModelMixin
from .search_slug_model_mixin import SearchSlugModelMixin


class Manager(HouseholdStructureManager, SearchSlugManager):
    pass


class HouseholdStructure(EnrollmentModelMixin, EnumerationModelMixin,
                         SurveyScheduleModelMixin, SearchSlugModelMixin,
                         BaseUuidModel):

    """A system model that links a household to its household members
    for a given survey year and helps track the enrollment status, enumeration
    status, enumeration attempts and other system values. """

    household = models.ForeignKey(Household, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date")

    progress = models.CharField(
        verbose_name='Progress',
        max_length=25,
        default='Not Started',
        null=True,
        editable=False)

    note = models.CharField("Note", max_length=250, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.survey_schedule,) + self.household.natural_key()
    natural_key.dependencies = ['household.household']

    def __str__(self):
        return '{} for {}'.format(self.household, self.survey_schedule)

    def save(self, *args, **kwargs):
        if not self.id and not self.report_datetime:
            # household creates household_structure, so use
            # household.report_datetime.
            self.report_datetime = self.household.report_datetime
        super().save(*args, **kwargs)

    @property
    def next(self):
        """Returns the next household structure instance or None in
        the survey_schedule sequence."""
        try:
            next_obj = next(SurveyScheduleIterator(
                model_obj=self, household=self.household))
        except StopIteration:
            next_obj = None
        return next_obj

    @property
    def previous(self):
        """Returns the previous household structure instance or None
        in the survey_schedule sequence."""
        if self.survey_schedule_object.previous:
            return self.household.householdstructure_set.filter(
                survey_schedule=self.survey_schedule_object.previous.field_value).first()
        else:
            return None

    @property
    def last(self):
        """Returns the last household structure instance in
        the survey_schedule sequence.
        """
        survey_schedule_object = self.survey_schedule_object.next
        while survey_schedule_object:
            print(survey_schedule_object)
            last_household_structure = self.household.householdstructure_set.filter(
                survey_schedule=survey_schedule_object.field_value).first()
            survey_schedule_object = survey_schedule_object.next
        return last_household_structure or self

    class Meta:
        unique_together = ('household', 'survey_schedule')
        ordering = ('household', 'survey_schedule')
