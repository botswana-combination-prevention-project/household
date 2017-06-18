from django.apps import apps as django_apps

from edc_model_wrapper import ModelWrapper


class HouseholdModelWrapper(ModelWrapper):

    model_name = 'household.household'
    next_url_name = django_apps.get_app_config('household').listboard_url_name
    extra_querystring_attrs = {'household.household': ['plot']}
    next_url_attrs = {'household.household': ['household_identifier']}
    url_instance_attrs = ['household_identifier', 'plot']

    @property
    def plot(self):
        return self.object.plot.id
