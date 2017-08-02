from django.db import models
from django_crypto_fields.fields import EncryptedTextField

from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_search.model_mixins import SearchSlugModelMixin as BaseSearchSlugModelMixin
from edc_search.model_mixins import SearchSlugManager

from plot.models import Plot

from ..managers import HouseholdManager


class Manager(HouseholdManager, SearchSlugManager):
    pass


class SearchSlugModelMixin(BaseSearchSlugModelMixin):

    def get_search_slug_fields(self):
        return [
            'household_identifier',
            'plot.plot_identifier',
            'plot.map_area']

    class Meta:
        abstract = True


class HouseholdIdentifierModelMixin(models.Model):
    """Mixin to allocate a household identifier.
    """

    household_identifier = models.CharField(
        verbose_name='Household Identifier',
        max_length=25,
        unique=True,
        editable=False)

    household_sequence = models.IntegerField(
        editable=False,
        null=True,
        help_text=('is 1 for first household in plot, 2 for second, 3, etc. '
                   'Embedded in household identifier.'))

    def save(self, *args, **kwargs):
        if not self.id:
            self.household_identifier = '{}-{}'.format(
                self.plot.plot_identifier, str(self.household_sequence).rjust(2, '0'))
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Household(HouseholdIdentifierModelMixin, SearchSlugModelMixin, BaseUuidModel):
    """A system model that represents the household asset.
    See also HouseholdStructure.
    """

    plot = models.ForeignKey(Plot, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name='Report Date/Time',
        default=get_utcnow)

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

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.household_identifier

    def save(self, *args, **kwargs):
        if not self.id:
            # plots create households, so use plot.report_datetime.
            self.report_datetime = self.plot.report_datetime
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.household_identifier, ) + self.plot.natural_key()
    natural_key.dependencies = ['plot.plot']

    class Meta:
        ordering = ['-household_identifier', ]
