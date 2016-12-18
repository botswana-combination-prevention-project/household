from faker import Faker
from model_mommy.recipe import Recipe

from .models import Household, HouseholdLog, HouseholdLogEntry

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
