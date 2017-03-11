from faker import Faker

from plot.utils import get_anonymous_plot

from .models import Household, HouseholdStructure

fake = Faker()


def get_anonymous_household_structure(survey_schedule_name):
    plot = get_anonymous_plot()
    household = Household.objects.get(plot=plot)
    return HouseholdStructure.objects.get(
        household=household,
        householdsurvey_schedule=survey_schedule_name)
