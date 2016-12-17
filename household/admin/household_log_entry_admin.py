from django.contrib import admin

from ..admin_site import household_admin
from ..forms import HouseholdLogEntryForm
from ..models import HouseholdLogEntry, HouseholdLog

from .modeladmin_mixins import ModelAdminMixin


@admin.register(HouseholdLogEntry, site=household_admin)
class HouseholdLogEntryAdmin(ModelAdminMixin):
    form = HouseholdLogEntryForm
    date_hierarchy = 'modified'
    list_per_page = 15
    fields = ('household_log', 'report_datetime', 'household_status',
              'next_appt_datetime', 'next_appt_datetime_source', 'comment')
    list_display = ('household_log', 'report_datetime', 'next_appt_datetime')
    list_filter = (
        'report_datetime',
        'household_log__household_structure__survey',
        'next_appt_datetime',
        'household_log__household_structure__household__plot__map_area')
    radio_fields = {
        "next_appt_datetime_source": admin.VERTICAL,
        "household_status": admin.VERTICAL,
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "household_log":
            if request.GET.get('household_log'):
                kwargs["queryset"] = HouseholdLog.objects.filter(id__exact=request.GET.get('household_log', 0))
            else:
                self.readonly_fields = list(self.readonly_fields)
                try:
                    self.readonly_fields.index('household_log')
                except ValueError:
                    self.readonly_fields.append('household_log')
        return super(HouseholdLogEntryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class HouseholdLogEntryInline(admin.TabularInline):
    model = HouseholdLogEntry
    extra = 0
    max_num = 5
