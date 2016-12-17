from django.contrib import admin

from ..forms import HouseholdForm

from ..admin_site import household_admin
from ..models import Household

from .modeladmin_mixins import ModelAdminMixin


@admin.register(Household, site=household_admin)
class HouseholdAdmin(ModelAdminMixin):

    form = HouseholdForm
    list_per_page = 30
    list_max_show_all = 1000

    instructions = []

    list_display = ('household_identifier', 'plot', 'created', 'modified')

    list_filter = ('created', 'modified', 'plot__map_area', 'hostname_modified')

    search_fields = ('household_identifier', 'plot__map_area', 'id', 'plot__id')

    readonly_fields = ('plot', 'household_identifier', )
