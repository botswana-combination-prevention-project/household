from django.db import models

from .enumeration_helper import EnumerationHelper


class HouseholdStructureManager(models.Manager):

    to_reference_model = ['household', 'plot']

    def get_by_natural_key(self, household_identifier, survey_name):
        return self.get(household__household_identifier=household_identifier, survey__survey_name=survey_name)

    def add_household_members_from_survey(self, household, source_survey, target_survey):
        """Adds household members from a previous survey to an
        unenumerated household structure of a new survey."""
        enumeration_helper = EnumerationHelper(household, source_survey, target_survey)
        return enumeration_helper.add_members_from_survey()


class HouseholdManager(models.Manager):

    def get_by_natural_key(self, household_identifier):
        return self.get(household_identifier=household_identifier)


class HouseholdLogManager(models.Manager):

    def get_by_natural_key(self, household_identifier):
        return self.get(household_identifier=household_identifier)


class HouseholdAssessmentManager(models.Manager):

    def get_by_natural_key(self, household_structure):
        return self.get(household_structure=household_structure)


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


class HouseholdRefusalManager(models.Manager):

    def get_by_natural_key(self, household_structure):
        return self.get(household_structure=household_structure)


class HouseholdWorkListManager(models.Manager):

    def get_by_natural_key(self, household_structure, label):
        return self.get(household_structure=household_structure, label=label)


class HouseholdRefusalHistoryManager(models.Manager):

    def get_by_natural_key(self, household_structure, transaction):
        return self.get(household_structure=household_structure, transaction=transaction)
