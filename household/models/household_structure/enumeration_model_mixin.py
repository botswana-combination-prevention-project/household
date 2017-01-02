from django.apps import apps as django_apps
from django.db import models

from ...exceptions import HouseholdEnumerationError

from .utils import is_failed_enumeration_attempt


class EnumerationModelMixin(models.Model):

    enumerated = models.BooleanField(
        default=False,
        editable=False,
        help_text='Set to True when first household_member is enumerated')

    enumeration_attempts = models.IntegerField(
        default=0,
        editable=False,
        help_text=('Updated by a signal on HouseholdLogEntry. '
                   'Number of attempts to enumerate a household_structure.'))

    failed_enumeration_attempts = models.IntegerField(
        default=0,
        editable=False,
        help_text=('Updated by a signal on HouseholdLogEntry. Number of failed attempts to'
                   'enumerate a household_structure.'))

    failed_enumeration = models.BooleanField(
        default=False,
        editable=False,
        help_text='Updated by household assessment save method only')

    refused_enumeration = models.BooleanField(
        default=False,
        editable=False,
        help_text='Updated by household enumeration refusal form')

    no_informant = models.BooleanField(
        default=False,
        editable=False,
        help_text='Updated by household assessment save method only')

    eligible_members = models.BooleanField(
        default=False,
        editable=False,
        help_text='Updated by household member save method and post_delete')

    def common_clean(self):
        app_config = django_apps.get_app_config('household')
        enumeration_attempts, failed_enumeration_attempts = self.updated_enumeration_attempts()
        if app_config.max_enumeration_attempts > 0:
            if enumeration_attempts > app_config.max_enumeration_attempts:
                raise HouseholdEnumerationError(
                    'Household may not be enumerated. Enumeration attempts exceeds 3. Got {}'.format(
                        enumeration_attempts))
        if failed_enumeration_attempts > app_config.max_failed_enumeration_attempts:
            raise HouseholdEnumerationError(
                'Household may not be enumerated. Failed attempts exceeds 3. Got {}'.format(
                    failed_enumeration_attempts))
        super().common_clean()

    def save(self, *args, **kwargs):
        self.enumeration_attempts, self.failed_enumeration_attempts = self.updated_enumeration_attempts()
        super().save(*args, **kwargs)

    def updated_enumeration_attempts(self):
        """Returns tuple of the number of (successful, failed) enumeration attempts."""
        enumeration_attempts, failed_enumeration_attempts = (
            self.enumeration_attempts or 0, self.failed_enumeration_attempts or 0)
        if not self.enumerated:
            HouseholdLogEntry = django_apps.get_model('household.householdlogentry')
            household_log_entrys = HouseholdLogEntry.objects.filter(household_log__household_structure=self)
            enumeration_attempts = household_log_entrys.count()
            failed_enumeration_attempts = len(
                [obj for obj in household_log_entrys if is_failed_enumeration_attempt(obj)])
        return (enumeration_attempts, failed_enumeration_attempts)

    class Meta:
        abstract = True
