from edc_model_wrapper import ModelWithLogWrapper, ModelRelation

from .household_log_entry_model_wrapper import HouseholdLogEntryModelWrapper
from .household_model_wrapper import HouseholdModelWrapper
from .household_structure_model_wrapper import HouseholdStructureModelWrapper


class HouseholdLogModelRelation(ModelRelation):

    def __init__(self, model_obj=None, ordering=None, **kwargs):
        self.ordering = ordering or '-report_datetime'
        self.model_obj = model_obj
        self.models = [model_obj.__class__]
        self.model_names = []
        self.log = model_obj.householdlog
        self.log_model = model_obj.householdlog.__class__
        self.log_entries = model_obj.householdlog.householdlogentry_set.all().order_by(
            self.ordering)
        self.log_entry_model = self.log_entries.model
        try:
            self.log_entry = model_obj.householdlog.householdlogentry_set.order_by(
                self.ordering)[0]
        except IndexError:
            self.log_entry = self.log_entry_model(household_log=self.log)
        else:
            self.log_entry_model = self.log_entry.__class__
        self.models.append(self.log_model)
        self.models.append(self.log_entry_model)
        self.model_names.append(self.log_model._meta.model_name)
        self.model_names.append(self.log_entry_model._meta.model_name)


class HouseholdStructureWithLogEntryWrapper(ModelWithLogWrapper):

    model = 'household.householdstructure'
    model_wrapper_cls = HouseholdStructureModelWrapper
    log_entry_model_wrapper_cls = HouseholdLogEntryModelWrapper
    model_relation_cls = HouseholdLogModelRelation
    next_url_name = 'household_dashboard:listboard_url'
    next_url_attrs = ['household_identifier',
                      'survey_schedule', 'plot_identifier']
    querystring_attrs = ['community_name', 'household']

    @property
    def plot_identifier(self):
        return self.object.household.plot.plot_identifier

    @property
    def community_name(self):
        return ' '.join(self.object.household.plot.map_area.split('_'))

    @property
    def household_identifier(self):
        return self.object.household.household_identifier

    @property
    def survey_schedule_object(self):
        return self.object.survey_schedule_object

    @property
    def household(self):
        return HouseholdModelWrapper(self.object.household)
