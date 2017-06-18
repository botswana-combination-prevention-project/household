from django.apps import apps as django_apps
from django.db import models

from ...exceptions import HouseholdEnumerationError


class EnumerationModelMixin(models.Model):

    enumerated = models.BooleanField(
        default=False,
        editable=False,
        help_text='Set to True when first household_member is enumerated')

    enumerated_datetime = models.DateTimeField(null=True)

    enumeration_attempts = models.IntegerField(
        default=0,
        editable=False,
        help_text=('Updated by a signal on HouseholdLogEntry. '
                   'Number of attempts to enumerate a household_structure.'))

    failed_enumeration_attempts = models.IntegerField(
        default=0,
        editable=False,
        help_text=('Updated by a signal on HouseholdLogEntry.'
                   'Number of failed attempts to enumerate a '
                   'household_structure.'))

    failed_enumeration = models.BooleanField(
        default=False,
        editable=False,
        help_text='Updated by household assessment save method ONLY')

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
        if app_config.max_enumeration_attempts > 0:
            if self.enumeration_attempts > app_config.max_enumeration_attempts:
                raise HouseholdEnumerationError(
                    'Household may not be enumerated. Enumeration attempts exceeds 3. Got {}'.format(
                        self.enumeration_attempts))
        if self.failed_enumeration_attempts > app_config.max_failed_enumeration_attempts:
            raise HouseholdEnumerationError(
                'Household may not be enumerated. Failed attempts exceeds 3. Got {}'.format(
                    self.failed_enumeration_attempts))
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [HouseholdEnumerationError]

    class Meta:
        abstract = True
