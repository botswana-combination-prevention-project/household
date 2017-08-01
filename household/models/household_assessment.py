from django.db import models

from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_validators import datetime_not_future
from edc_base.utils import get_utcnow
from edc_constants.choices import YES_NO_DONT_KNOW

from ..choices import RESIDENT_LAST_SEEN
from ..exceptions import HouseholdAssessmentError, HouseholdAlreadyEnumeratedError
from ..managers import HouseholdAssessmentManager
from .household_structure import HouseholdStructure


class HouseholdAssessment(BaseUuidModel):

    """A model completed by the user to assess a household that could not
    be enumerated.

    Requires three failed enumeration attempts before it can be completed.
    """

    household_structure = models.OneToOneField(
        HouseholdStructure, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=get_utcnow,
        validators=[datetime_not_future])

    potential_eligibles = models.CharField(
        verbose_name=(
            'Research Assistant: From speaking with the respondent, '
            'is at least one member of this plot potentially eligible?'),
        choices=YES_NO_DONT_KNOW,
        max_length=25,
        null=True,
        editable=True)

    eligibles_last_seen_home = models.CharField(
        verbose_name=('When was a resident last seen in this household?'),
        choices=RESIDENT_LAST_SEEN,
        max_length=25,
        null=True,
        blank=True,
        editable=True)

    objects = HouseholdAssessmentManager()

    history = HistoricalRecords()

    def __str__(self):
        return str(self.household_structure)

    def natural_key(self):
        return self.household_structure.natural_key()
    natural_key.dependencies = ['household.household_structure']

    def common_clean(self):
        if self.household_structure.enumerated:
            raise HouseholdAlreadyEnumeratedError(
                f'{self._meta.verbose_name} is not required. Household '
                'has already been enumerated.')
        elif self.household_structure.failed_enumeration_attempts < 3:
            failed_attempts = self.household_structure.failed_enumeration_attempts
            raise HouseholdAssessmentError(
                f'{self._meta.verbose_name} is not required, yet. Make 3 '
                f'unsuccessful enumeration attempts first. Got '
                f'failed_enumeration_attempts={failed_attempts}')
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [
            HouseholdAlreadyEnumeratedError, HouseholdAssessmentError]

    class Meta:
        verbose_name = 'Household Residency Status'
        verbose_name_plural = 'Household Residency Status'
