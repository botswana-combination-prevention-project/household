from django.apps import apps as django_apps

from edc_model_wrapper import ModelWrapper


class HouseholdLogEntryModelWrapper(ModelWrapper):

    model_name = 'household.householdlogentry'
    next_url_name = django_apps.get_app_config('household').listboard_url_name
    extra_querystring_attrs = {
        'household.householdlogentry': ['household_log']}
    next_url_attrs = {'household.householdlogentry':
                      ['household_identifier', 'survey_schedule']}
    url_instance_attrs = [
        'household_log', 'household_identifier', 'survey_schedule']

    @property
    def household_log(self):
        return self.object.household_log

    @property
    def household_identifier(self):
        return self.household_log.household_structure.household.household_identifier

    @property
    def survey_schedule(self):
        return self.survey_schedule_object.field_value

    @property
    def survey_schedule_object(self):
        return self.object.household_log.household_structure.survey_schedule_object
