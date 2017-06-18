from edc_model_wrapper import ModelWithLogWrapper

from .household_log_entry_model_wrapper import HouseholdLogEntryModelWrapper
from .household_model_wrapper import HouseholdModelWrapper
from .household_structure_model_wrapper import HouseholdStructureModelWrapper


class HouseholdStructureWithLogEntryWrapper(ModelWithLogWrapper):

    model_wrapper_class = HouseholdStructureModelWrapper
    log_entry_model_wrapper_class = HouseholdLogEntryModelWrapper
    # e.g. HouseholdLog not HouseholdStructureLog
    log_model_attr_prefix = 'household'

    @property
    def plot_identifier(self):
        return self.parent.object.household.plot.plot_identifier

    @property
    def community_name(self):
        return ' '.join(self.parent.object.household.plot.map_area.split('_'))

    @property
    def household_identifier(self):
        return self.parent.object.household.household_identifier

    @property
    def survey_schedule_object(self):
        return self.parent.object.survey_schedule_object

    @property
    def household(self):
        return HouseholdModelWrapper(self.parent.object.household)
