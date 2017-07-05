import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style
from django.conf import settings

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'household'
    listboard_template_name = 'household_dashboard/listboard.html'
    listboard_url_name = 'household_dashboard:listboard_url'
    base_template_name = 'edc_base/base.html'
    admin_site_name = 'household_admin'
    max_household_log_entries = 0  # 0 means unlimited
    max_failed_enumeration_attempts = 5

    @property
    def max_enumeration_attempts(self):
        return self.max_household_log_entries

    def ready(self):
        from household.signals import (
            create_household_structures_on_post_save,
            household_structure_on_post_save,
            household_log_on_post_save,
            household_refusal_on_post_save,
            household_assessment_on_post_save,
            household_refusal_on_delete,
            household_assessment_on_delete,
            household_log_entry_on_post_save,
            household_log_entry_on_post_delete)
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        sys.stdout.write(' * max_household_log_entries: \'{}\'\n'.format(
            self.max_household_log_entries or 'unlimited'))
        sys.stdout.write(' * max_failed_enumeration_attempts: \'{}\'\n'.format(
            self.max_failed_enumeration_attempts or 'unlimited'))
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')


if settings.APP_NAME == 'household':

    from edc_map.apps import AppConfig as BaseEdcMapAppConfig

    class EdcMapAppConfig(BaseEdcMapAppConfig):
        verbose_name = 'Test Mappers'
        mapper_model = 'plot.plot'
        landmark_model = []
        verify_point_on_save = False
        zoom_levels = ['14', '15', '16', '17', '18']
        identifier_field_attr = 'plot_identifier'
        extra_filter_field_attr = 'enrolled'
