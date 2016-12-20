from django.db import models

from .enumeration_helper import EnumerationHelper


class HouseholdStructureManager(models.Manager):

    to_reference_model = ['household', 'plot']

    def get_by_natural_key(self, survey, household_identifier, plot_identifier):
        return self.get(
            survey=survey,
            household__household_identifier=household_identifier,
            household__plot__plot_identifier=plot_identifier,
        )

    def add_household_members_from_survey(self, household, source_survey, target_survey):
        """Adds household members from a previous survey to an
        unenumerated household structure of a new survey."""
        enumeration_helper = EnumerationHelper(household, source_survey, target_survey)
        return enumeration_helper.add_members_from_survey()


class HouseholdManager(models.Manager):

    def get_by_natural_key(self, household_identifier, plot_identifier):
        return self.get(household_identifier=household_identifier, plot__plot_identifier=plot_identifier)


class HouseholdLogManager(models.Manager):

    def get_by_natural_key(self, survey, household_identifier, plot_identifier):
        return self.get(
            household_structure__survey=survey,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=plot_identifier,
        )


class HouseholdAssessmentManager(models.Manager):

    def get_by_natural_key(self, survey, household_identifier, plot_identifier):
        return self.get(
            household_structure__survey=survey,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=plot_identifier,
        )


class LogEntryManager(models.Manager):

    to_reference_model = ['household_log', 'household_structure', 'household', 'plot']

    def get_by_natural_key(self, report_datetime, survey, household_identifier, plot_identifier):
        return self.get(
            report_datetime=report_datetime,
            household_log__household_structure__survey=survey,
            household_log__household_structure__household__household_identifier=household_identifier,
            household_log__household_structure__household__plot__plot_identifier=plot_identifier,
        )


class HistoryManager(models.Manager):

    def get_by_natural_key(self, transaction):
        return self.get(transaction=transaction)


class HouseholdRefusalManager(models.Manager):

    def get_by_natural_key(self, survey, household_identifier, plot_identifier):
        return self.get(
            household_structure__survey=survey,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=plot_identifier,
        )


class HouseholdWorkListManager(models.Manager):

    def get_by_natural_key(self, label, survey, household_identifier, plot_identifier):
        return self.get(
            label=label,
            household_structure__survey=survey,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=plot_identifier,
        )


class HouseholdRefusalHistoryManager(models.Manager):

    def get_by_natural_key(self, transaction, survey, household_identifier, plot_identifier):
        return self.get(
            transaction=transaction,
            household_structure__survey=survey,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=plot_identifier,
        )
