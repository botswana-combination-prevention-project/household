from django.db import models

from bcpp.manager_mixins import BcppSubsetManagerMixin

from .enumeration_helper import EnumerationHelper


class HouseholdStructureManager(BcppSubsetManagerMixin, models.Manager):

    to_reference_model = ['household', 'plot']

    def get_by_natural_key(self, household_identifier, survey_name):
        return self.get(household__household_identifier=household_identifier, survey__survey_name=survey_name)

    def add_household_members_from_survey(self, household, source_survey, target_survey):
        """Adds household members from a previous survey to an
        unenumerated household structure of a new survey."""
        enumeration_helper = EnumerationHelper(household, source_survey, target_survey)
        return enumeration_helper.add_members_from_survey()


class HouseholdManager(BcppSubsetManagerMixin, models.Manager):

    to_reference_model = ['plot']

    def get_by_natural_key(self, household_identifier):
        return self.get(household_identifier=household_identifier)


class LogEntryManager(models.Manager):

    to_reference_model = ['household_log', 'household_structure', 'household', 'plot']

    def get_by_natural_key(self, report_datetime, household_identifier, survey_name):
        return self.get(
            report_datetime=report_datetime,
            household_structure__household__household_identifier=household_identifier,
            household_structure__survey__survey_name=survey_name)


class HistoryManager(models.Manager):

    def get_by_natural_key(self, transaction):
        return self.get(transaction=transaction)

