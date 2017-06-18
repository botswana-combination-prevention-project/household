from django.apps import apps as django_apps

from edc_model_wrapper import ModelWrapper


class HouseholdStructureModelWrapper(ModelWrapper):

    model_name = 'household.householdstructure'
    next_url_name = django_apps.get_app_config('household').listboard_url_name
    extra_querystring_attrs = {
        'household.householdstructure': ['plot_identifier']}
    next_url_attrs = {'household.householdstructure':
                      ['household_identifier', 'survey_schedule']}
    url_instance_attrs = [
        'household_identifier', 'survey_schedule', 'plot_identifier']

    @property
    def household_identifier(self):
        return self.object.household.household_identifier

    @property
    def plot_identifier(self):
        return self.object.household.plot.plot_identifier
