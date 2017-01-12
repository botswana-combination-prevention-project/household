from django.contrib import admin

from ..admin_site import household_admin
from ..forms import HouseholdLogForm
from ..models import HouseholdLog

from .household_log_entry_admin import HouseholdLogEntryInline
from .modeladmin_mixins import ModelAdminMixin


@admin.register(HouseholdLog, site=household_admin)
class HouseholdLogAdmin(ModelAdminMixin):
    form = HouseholdLogForm

    instructions = []
    inlines = [HouseholdLogEntryInline, ]
    date_hierarchy = 'modified'
    list_per_page = 15

    list_display = ('household_structure', 'modified', 'user_modified', 'hostname_modified')

    search_fields = (
        'household_structure__household__household_identifier',
        'household_structure__id',
        'household_structure__household__plot__plot_identifier')

    list_filter = ('household_structure__survey_schedule', 'hostname_created', 'created')

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + ('household_structure', )
