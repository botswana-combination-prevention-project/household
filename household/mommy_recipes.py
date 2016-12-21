from django.apps import apps as django_apps
from faker import Faker
from model_mommy.recipe import Recipe

from .models import Household, HouseholdLog, HouseholdLogEntry, HouseholdRefusal, HouseholdAssessment


def get_utcnow():
    return django_apps.get_app_config('edc_base_test').get_utcnow()

fake = Faker()

household = Recipe(
    Household,
)


householdlog = Recipe(
    HouseholdLog,
)


householdlogentry = Recipe(
    HouseholdLogEntry,
)


householdrefusal = Recipe(
    HouseholdRefusal,
)


householdassessment = Recipe(
    HouseholdAssessment,
)
