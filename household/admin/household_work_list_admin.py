from django.contrib import admin

from ..admin_site import household_admin
from ..forms import HouseholdWorkListForm
from ..models import HouseholdWorkList
from .modeladmin_mixins import ModelAdminMixin


@admin.register(HouseholdWorkList, site=household_admin)
class HouseholdWorkListAdmin(ModelAdminMixin):

    form = HouseholdWorkListForm
    date_hierarchy = 'visit_date'
    list_per_page = 15

    fields = (
        'household_structure',
        'note')

    list_display = (
        'household_structure',
        # 'plot',
        # 'survey_schedule',
        'label',
        # 'composition',
        # 'call_list',
        # 'appt',
        'visit_date',
        'status',
        'appt_count',
        'enrolled_type',
        'members',
        'bhs',
        'hic',
        'log_attempts',
        'log_date',
        'log_status',
        'modified',
        'user_modified')

    list_filter = (
        'household_structure__survey_schedule',
        'label',
        'visit_date',
        'status',
        'appt_count',
        'enrolled_type',
        'log_attempts',
        'log_date',
        'log_status',
        'members',
        'bhs',
        'hic',
        'user_modified',
        'hostname_modified',
    )
    search_fields = (
        'household_structure__household__plot__plot_identifier',
        'household_structure__household__household_identifier',
        'household_structure__household__id',
        'household_structure__id',
        'id',)

    readonly_fields = ('household_structure', )
