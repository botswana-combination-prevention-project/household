from django.db import models
from django_crypto_fields.fields import EncryptedTextField

from edc_base.model.models import BaseUuidModel, HistoricalRecords

from plot.models import Plot


class Household(BaseUuidModel):
    """A system model that represents the household asset. See also HouseholdStructure."""

    plot = models.ForeignKey(Plot, null=True)

    report_datetime = models.DateTimeField(
        verbose_name='Report Date/Time',
        null=True)

    household_identifier = models.CharField(
        verbose_name='Household Identifier',
        max_length=25,
        unique=True,
        help_text="Household identifier",
        null=True,
        editable=False)

    household_sequence = models.IntegerField(
        editable=False,
        null=True,
        help_text=('is 1 for first household in plot, 2 for second, 3, etc. '
                   'Embedded in household identifier.'))

    comment = EncryptedTextField(
        max_length=250,
        help_text="You may provide a comment here or leave BLANK.",
        blank=True,
        null=True)

    # updated by subject_consent save method
    enrolled = models.BooleanField(
        default=False,
        editable=False,
        help_text=('Set to true if one member is consented. '
                   'Updated by Household_structure post_save.'))

    enrolled_datetime = models.DateTimeField(
        null=True,
        editable=False,
        help_text=('datetime that household is enrolled. '
                   'Updated by Household_structure post_save.'))

    # objects = HouseholdManager()

    history = HistoricalRecords()

    def __str__(self):
        return self.household_identifier

    def natural_key(self):
        return (self.household_identifier, )

    def gps(self):
        return "S{0} {1} E{2} {3}".format(
            self.gps_degrees_s, self.gps_minutes_s, self.gps_degrees_e, self.gps_minutes_e)

    class Meta:
        app_label = 'household'
        ordering = ['-household_identifier', ]
