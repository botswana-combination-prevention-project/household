from django.db import models
from django.urls.base import reverse

from edc_base.model.models import BaseUuidModel, HistoricalRecords

from .household_structure import HouseholdStructure


class HouseholdLog(BaseUuidModel):
    """A system model that links the household log to the household."""

    household_structure = models.OneToOneField(HouseholdStructure)

    # objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return str(self.household_structure)

    def natural_key(self):
        return self.household_structure.natural_key()
    natural_key.dependencies = ['household.household_structure', ]

    @property
    def todays_household_log_entries(self):
        """Confirms there is an househol_log_entry for today."""
        # TODO: do this somewhere else
        raise
#         today = date.today()
#         return HouseholdLogEntry.objects.filter(
#             household_log=self,
#             report_datetime__year=today.year,
#             report_datetime__month=today.month,
#             report_datetime__day=today.day)

    def structure(self):
        url = '{}?q={1}'.format(reverse('household_admin:household_structure'), self.household_structure.pk)
        return """<a href="{url}" />structure</a>""".format(url=url)
    structure.allow_tags = True

    class Meta:
        app_label = 'household'
