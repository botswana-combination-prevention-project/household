from faker import Faker
from model_mommy.recipe import Recipe

from edc_base.test_mixins.reference_date_mixin import ReferenceDateMixin

from .models import Household, HouseholdLog, HouseholdLogEntry, HouseholdRefusal, HouseholdAssessment


class ReferenceDate(ReferenceDateMixin):
    consent_model = 'example_survey.subjectconsent'


def get_utcnow():
    return ReferenceDate().get_utcnow()

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
