from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel

from ..exceptions import FormNotRequiredError

from ..managers import HouseholdRefusalManager

from .model_mixins import HouseholdRefusalMixin
from household.constants import REFUSED_ENUMERATION


class HouseholdRefusal(HouseholdRefusalMixin, BaseUuidModel):
    """A model completed by the user to indicate the reason why a household
    cannot be enumerated.
    """

    objects = HouseholdRefusalManager()

    history = HistoricalRecords()

    def common_clean(self):
        household_log = self.household_structure.householdlog
        if household_log.last_log_status != REFUSED_ENUMERATION:
            raise FormNotRequiredError(
                f'Form not required. {self._meta.verbose_name} is only required '
                f'if the household was last reported as having refused enumeration. '
                f'Got \'{household_log.get_last_log_status_display}\'.')
        super().common_clean()

    def natural_key(self):
        return self.household_structure.natural_key()
    natural_key.dependencies = ['household.household_structure']

    class Meta:
        app_label = 'household'
        ordering = ['household_structure', ]
