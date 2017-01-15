from django.apps import apps as django_apps

from edc_dashboard.wrappers import ModelWrapper, ModelWithLogWrapper


class HouseholdModelWrapper(ModelWrapper):

    model_name = 'household.household'
    admin_site_name = 'household_admin'
    url_namespace = 'household'
    next_url_name = django_apps.get_app_config('household').listboard_url_name
    extra_querystring_attrs = {'household.household': ['plot']}
    next_url_attrs = {'household.household': ['household_identifier']}
    url_instance_attrs = ['household_identifier', 'plot']

    @property
    def plot(self):
        return self._original_object.plot.id


class HouseholdStructureModelWrapper(ModelWrapper):

    model_name = 'household.householdstructure'
    admin_site_name = 'household_admin'
    url_namespace = 'household'
    next_url_name = django_apps.get_app_config('household').listboard_url_name
    extra_querystring_attrs = {'household.householdstructure': ['plot_identifier']}
    next_url_attrs = {'household.householdstructure': ['household_identifier', 'survey_schedule']}
    url_instance_attrs = ['household_identifier', 'survey_schedule', 'plot_identifier']

    @property
    def household_identifier(self):
        return self._original_object.household.household_identifier

    @property
    def plot_identifier(self):
        return self._original_object.household.plot.plot_identifier


class HouseholdLogEntryWrapper(ModelWrapper):

    model_name = 'household.householdlogentry'
    admin_site_name = 'household_admin'
    url_namespace = 'household'
    next_url_name = django_apps.get_app_config('household').listboard_url_name
    extra_querystring_attrs = {'household.householdlogentry': ['household_log']}
    next_url_attrs = {'household.householdlogentry': ['household_identifier', 'survey_schedule']}
    url_instance_attrs = ['household_log', 'household_identifier', 'survey_schedule']

    @property
    def household_identifier(self):
        return self._original_object.household_log.household_structure.household.household_identifier

    @property
    def survey_schedule(self):
        return self.survey_schedule_object.field_value

    @property
    def survey_schedule_object(self):
        return self._original_object.household_log.household_structure.survey_schedule_object


class HouseholdStructureWithLogEntryWrapper(ModelWithLogWrapper):

    model_wrapper_class = HouseholdStructureModelWrapper
    log_entry_model_wrapper_class = HouseholdLogEntryWrapper

    # its not household.household_structure_log but household.household_log
    parent_alias = 'household.household'

    @property
    def plot_identifier(self):
        return self.parent._original_object.household.plot.plot_identifier

    @property
    def community_name(self):
        return ' '.join(self.parent._original_object.household.plot.map_area.split('_'))

    @property
    def household_identifier(self):
        return self.parent._original_object.household.household_identifier

    @property
    def survey_schedule(self):
        return self.survey_schedule_object.field_value

    @property
    def survey_schedule_object(self):
        return self.parent._original_object.survey_schedule_object

    @property
    def household(self):
        return HouseholdModelWrapper(self.parent._original_object.household)
