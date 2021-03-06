from django.contrib import admin

from ..admin_site import household_admin
from ..forms import HouseholdRefusalForm
from ..models import HouseholdRefusal
from .modeladmin_mixins import ModelAdminMixin


@admin.register(HouseholdRefusal, site=household_admin)
class HouseholdRefusalAdmin(ModelAdminMixin):

    form = HouseholdRefusalForm
    date_hierarchy = 'modified'
    list_per_page = 30

    fields = (
        'household_structure',
        'report_datetime',
        'reason',
        'reason_other',
        'comment')

    radio_fields = {'reason': admin.VERTICAL}

    list_display = ('household_structure', 'report_datetime', 'created')

    list_filter = ('report_datetime', 'created',
                   'household_structure__household__plot__map_area')

    search_fields = (
        'household_structure__household__household_identifier',
        'household_structure__household__plot__map_area',
        'id',
        'plot__id')
