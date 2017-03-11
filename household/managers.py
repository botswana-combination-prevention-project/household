from django.db import models


class HouseholdStructureManager(models.Manager):

    to_reference_model = ['household', 'plot']

    def get_by_natural_key(self, survey_schedule, household_identifier, plot_identifier):
        return self.get(
            survey_schedule=survey_schedule,
            household__household_identifier=household_identifier,
            household__plot__plot_identifier=plot_identifier,
        )


class HouseholdManager(models.Manager):

    def get_by_natural_key(self, household_identifier, plot_identifier):
        return self.get(household_identifier=household_identifier, plot__plot_identifier=plot_identifier)


class HouseholdLogManager(models.Manager):

    def get_by_natural_key(self, survey_schedule, household_identifier, plot_identifier):
        return self.get(
            household_structure__survey_schedule=survey_schedule,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=plot_identifier,
        )


class HouseholdAssessmentManager(models.Manager):

    def get_by_natural_key(self, survey_schedule, household_identifier, plot_identifier):
        return self.get(
            household_structure__survey_schedule=survey_schedule,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=plot_identifier,
        )


class LogEntryManager(models.Manager):

    to_reference_model = ['household_log', 'household_structure', 'household', 'plot']

    def get_by_natural_key(self, report_datetime, survey_schedule, household_identifier, plot_identifier):
        return self.get(
            report_datetime=report_datetime,
            household_log__household_structure__survey_schedule=survey_schedule,
            household_log__household_structure__household__household_identifier=household_identifier,
            household_log__household_structure__household__plot__plot_identifier=plot_identifier,
        )


class HistoryManager(models.Manager):

    def get_by_natural_key(self, transaction):
        return self.get(transaction=transaction)


class HouseholdRefusalManager(models.Manager):

    def get_by_natural_key(self, survey_schedule, household_identifier, plot_identifier):
        return self.get(
            household_structure__survey_schedule=survey_schedule,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=plot_identifier,
        )


class HouseholdWorkListManager(models.Manager):

    def get_by_natural_key(self, label, survey_schedule, household_identifier, plot_identifier):
        return self.get(
            label=label,
            household_structure__survey_schedule=survey_schedule,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=plot_identifier,
        )


class HouseholdRefusalHistoryManager(models.Manager):

    def get_by_natural_key(self, transaction, survey_schedule, household_identifier, plot_identifier):
        return self.get(
            transaction=transaction,
            household_structure__survey_schedule=survey_schedule,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=plot_identifier,
        )
