from django.contrib import admin

from .admin_site import household_admin
from .forms import HouseholdForm
from .admin_mixins import ModelAdminMixin
from .models import Household


@admin.register(Household, site=household_admin)
class HouseholdAdmin(ModelAdminMixin):

    form = HouseholdForm
    list_per_page = 30
    list_max_show_all = 100

    instructions = []

    list_display = ('household_identifier', 'structure', 'plot', 'community', 'created', 'modified')

    list_filter = ('created', 'modified', 'community', 'hostname_modified')

    search_fields = ('household_identifier', 'community', 'id', 'plot__id')

    readonly_fields = ('plot', 'household_identifier', )
