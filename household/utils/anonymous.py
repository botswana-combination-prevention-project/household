from django.apps import apps as django_apps

from plot.utils import get_anonymous_plot


def get_anonymous_household_structure(survey_schedule_name):
    plot = get_anonymous_plot()
    household_model_cls = django_apps.get_model('household.household')
    household_structure_model_cls = django_apps.get_model(
        'household.householdstructure')

    household = household_model_cls.objects.get(plot=plot)
    return household_structure_model_cls.objects.get(
        household=household,
        householdsurvey_schedule=survey_schedule_name)
