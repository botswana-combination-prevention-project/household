from django.contrib import admin

from ..admin_site import household_admin
from ..forms import HouseholdAssessmentForm
from ..models import HouseholdAssessment

from .modeladmin_mixins import ModelAdminMixin


@admin.register(HouseholdAssessment, site=household_admin)
class HouseholdAssessmentAdmin(ModelAdminMixin):

    form = HouseholdAssessmentForm

    fields = (
        'household_structure',
        'potential_eligibles',
        'eligibles_last_seen_home',
    )

    radio_fields = {
        'potential_eligibles': admin.VERTICAL,
        'eligibles_last_seen_home': admin.VERTICAL,
    }

    list_filter = ('household_structure__household__plot__map_area',)

    search_fields = (
        'household_structure__household__household_identifier',
        'household_structure__id',
        'household_structure__household__plot__plot_identifier')
