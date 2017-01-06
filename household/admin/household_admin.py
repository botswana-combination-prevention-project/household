from django.contrib import admin

from edc_base.modeladmin_mixins import audit_fieldset_tuple

from ..admin_site import household_admin
from ..forms import HouseholdForm
from ..models import Household

from .modeladmin_mixins import ModelAdminMixin


@admin.register(Household, site=household_admin)
class HouseholdAdmin(ModelAdminMixin):

    form = HouseholdForm
    list_select_related = ('plot', )
    list_per_page = 10

    instructions = []

    fieldsets = fieldsets = (
        (None, {'fields': (
            'plot',
            'household_identifier',
            'report_datetime',
            'comment')}),
        ('Enrollment', {
            'classes': ('collapse',),
            'fields': (
                'enrolled',
                'enrolled_datetime')}),
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + (
            'household_identifier', 'enrolled', 'enrolled_datetime')

    list_display = ('household_identifier', 'plot', 'created', 'modified')

    list_filter = ('created', 'modified', 'plot__map_area', 'hostname_modified')

    search_fields = ('household_identifier', 'plot__map_area', 'id', 'plot__id')
