import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'household'
    listboard_template_name = 'household/listboard.html'
    listboard_url_name = 'household:listboard_url'
    base_template_name = 'edc_base/base.html'
    max_household_log_entries = 0
    max_failed_enumeration_attempts = 5

    @property
    def max_enumeration_attempts(self):
        return self.max_household_log_entries

    def ready(self):
        from household.signals import (
            household_on_post_save, household_structure_on_post_save, household_log_on_post_save,
            household_refusal_on_post_save, household_assessment_on_post_save,
            household_refusal_on_delete, household_assessment_on_delete, household_log_entry_on_post_save,
            household_log_entry_on_post_delete)
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        sys.stdout.write(' * max_household_log_entries: \'{}\'\n'.format(
            self.max_household_log_entries or 'unlimited'))
        sys.stdout.write(' * max_failed_enumeration_attempts: \'{}\'\n'.format(
            self.max_failed_enumeration_attempts or 'unlimited'))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
