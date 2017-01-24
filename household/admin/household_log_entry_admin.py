from django.apps import apps as django_apps
from django.contrib import admin
from django.utils.html import format_html

from edc_base.modeladmin_mixins import (
    ModelAdminChangelistButtonMixin,
    audit_fieldset_tuple, audit_fields)

from ..admin_site import household_admin
from ..forms import HouseholdLogEntryForm
from ..models import HouseholdLogEntry, HouseholdLog

from .modeladmin_mixins import ModelAdminMixin
from survey.admin import (
    survey_schedule_fieldset_tuple,
    survey_schedule_fields)


@admin.register(HouseholdLogEntry, site=household_admin)
class HouseholdLogEntryAdmin(ModelAdminChangelistButtonMixin, ModelAdminMixin):
    form = HouseholdLogEntryForm
    date_hierarchy = 'modified'
    list_per_page = 15
    fieldsets = (
        (None, {
            'fields': (
                'household_log',
                'report_datetime',
                'household_status',
                'next_appt_datetime',
                'next_appt_datetime_source',
                'comment')}),
        survey_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    def get_readonly_fields(self, request, obj=None):
        return (super().get_readonly_fields(request, obj=obj)
                + survey_schedule_fields
                + audit_fields)

    list_display = (
        'household_log',
        'enumeration_button',
        'report_datetime',
        'next_appt_datetime')
    list_filter = (
        'report_datetime',
        'household_log__household_structure__survey_schedule',
        'next_appt_datetime',
        'household_log__household_structure__household__plot__map_area')
    radio_fields = {
        "next_appt_datetime_source": admin.VERTICAL,
        "household_status": admin.VERTICAL,
    }
    search_fields = (
        'household_log__household_structure__household__household_identifier',
        'household_log__household_structure__survey_schedule',
    )

    def enumeration_button(self, obj):
        listboard_url_name = django_apps.get_app_config(
            'enumeration').listboard_url_name
        return self.button(
            listboard_url_name,
            reverse_args=(
                obj.household_log.household_structure.household.household_identifier,
                obj.household_log.household_structure.survey_schedule),
            label=format_html(
                '<i class="fa fa-sitemap fa-lg"></i>&nbsp;') + 'Enumeration')
    enumeration_button.short_description = 'Enumeration'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "household_log":
            if request.GET.get('household_log'):
                kwargs["queryset"] = HouseholdLog.objects.filter(
                    id__exact=request.GET.get('household_log', 0))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class HouseholdLogEntryInline(admin.TabularInline):
    model = HouseholdLogEntry
    extra = 0
    max_num = 5
