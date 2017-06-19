from django.apps import apps as django_apps

from edc_model_wrapper import ModelWrapper


class HouseholdStructureModelWrapper(ModelWrapper):

    model = 'household.householdstructure'
    next_url_name = django_apps.get_app_config('household').listboard_url_name
    next_url_attrs = ['household_identifier', 'survey_schedule']
    querystring_attrs = ['plot_identifier']

    @property
    def household_identifier(self):
        return self.object.household.household_identifier

    @property
    def plot_identifier(self):
        return self.object.household.plot.plot_identifier

    @property
    def community_name(self):
        return ' '.join(self.object.household.plot.map_area.split('_'))

    @property
    def survey_schedule_object(self):
        return self.object.survey_schedule_object

    @property
    def household(self):
        return self.object.household
