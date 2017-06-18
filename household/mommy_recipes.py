from faker import Faker
from model_mommy.recipe import Recipe

from edc_base.utils import get_utcnow

from .models import Household, HouseholdLog, HouseholdLogEntry, HouseholdRefusal, HouseholdAssessment


fake = Faker()

household = Recipe(
    Household,
    report_datetime=get_utcnow,
)


householdlog = Recipe(
    HouseholdLog,
    report_datetime=get_utcnow,
)


householdlogentry = Recipe(
    HouseholdLogEntry,
    report_datetime=get_utcnow,
)


householdrefusal = Recipe(
    HouseholdRefusal,
    report_datetime=get_utcnow,
)


householdassessment = Recipe(
    HouseholdAssessment,
    report_datetime=get_utcnow,
)
