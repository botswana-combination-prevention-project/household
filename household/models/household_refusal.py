from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel

from ..constants import REFUSED_ENUMERATION
from ..exceptions import FormNotRequiredError

from ..managers import HouseholdRefusalManager

from .household_log import HouseholdLog
from .model_mixins import HouseholdRefusalMixin


class HouseholdRefusal(HouseholdRefusalMixin, BaseUuidModel):
    """A model completed by the user to indicate the reason why a household
    cannot be enumerated."""

    objects = HouseholdRefusalManager()

    history = HistoricalRecords()

    def common_clean(self):
        household_log = HouseholdLog.objects.get(
            household_structure=self.household_structure)
        if household_log.last_log_status != REFUSED_ENUMERATION:
            raise FormNotRequiredError(
                'Form is not required. {} is only required if the household '
                'was last reported as having refused enumeration. Got \'{}\'.').format(
                    self._meta.verbose_name, household_log.get_last_log_status_display())
        super().common_clean()

    def natural_key(self):
        return self.household_structure.natural_key()
    natural_key.dependencies = ['household.household_structure']

    class Meta:
        app_label = 'household'
        ordering = ['household_structure', ]
