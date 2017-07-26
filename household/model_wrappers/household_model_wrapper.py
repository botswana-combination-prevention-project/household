from django.apps import apps as django_apps

from edc_model_wrapper.wrappers import ModelWrapper


class HouseholdModelWrapper(ModelWrapper):

    model = 'household.household'
    next_url_name = django_apps.get_app_config(
        'household_dashboard').listboard_url_name
    querystring_attrs = ['plot']
    next_url_attrs = ['household_identifier']

    @property
    def plot(self):
        return self.object.plot.id
