from django.core.exceptions import ValidationError
from django.db import models

from django_crypto_fields.fields import EncryptedTextField, EncryptedCharField

from edc_base.model.validators.date import datetime_not_future
from edc_base.utils import get_utcnow

from ..choices import HOUSEHOLD_REFUSAL

from .household_structure import HouseholdStructure
from household.exceptions import HouseholdAlreadyEnrolledError


class HouseholdRefusalMixin(models.Model):

    household_structure = models.OneToOneField(HouseholdStructure, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=get_utcnow,
        validators=[datetime_not_future])

    reason = models.CharField(
        verbose_name='Please indicate the reason the household cannot be enumerated',
        max_length=25,
        choices=HOUSEHOLD_REFUSAL)

    reason_other = EncryptedCharField(
        verbose_name='If Other, specify',
        max_length=100,
        blank=True,
        null=True)

    comment = EncryptedTextField(
        max_length=250,
        help_text="You may provide a comment here or leave BLANK.",
        blank=True,
        null=True)

    def common_clean(self):
        if self.household_structure.enrolled:
            raise HouseholdAlreadyEnrolledError(
                'Household is already enrolled. Blocking attempt to add \'{}\'.'.format(self._meta.verbose_name))
        super().common_clean()

    def save(self, *args, **kwargs):
        if self.household_structure.enrolled:
            raise ValidationError('Household is enrolled.')
        super(HouseholdRefusalMixin, self).save(*args, **kwargs)

    def __str__(self):
        return '{} ({})'.format(self.household_structure, self.report_datetime.strftime('%Y-%m-%d'))

    class Meta:
        abstract = True
