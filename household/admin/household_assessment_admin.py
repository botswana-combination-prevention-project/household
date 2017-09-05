from django.contrib import admin

from edc_base.modeladmin_mixins import (
    ModelAdminChangelistButtonMixin,
    audit_fieldset_tuple, audit_fields)

from ..admin_site import household_admin
from ..forms import HouseholdAssessmentForm
from ..models import HouseholdAssessment, HouseholdStructure
from .modeladmin_mixins import ModelAdminMixin


@admin.register(HouseholdAssessment, site=household_admin)
class HouseholdAssessmentAdmin(ModelAdminChangelistButtonMixin, ModelAdminMixin):

    form = HouseholdAssessmentForm

    fieldsets = (
        (None, {
            'fields': (
                'household_structure',
                'potential_eligibles',
                'eligibles_last_seen_home',)}),
        audit_fieldset_tuple,
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

    def get_readonly_fields(self, request, obj=None):
        return (super().get_readonly_fields(request, obj=obj) + audit_fields)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "household_structure":
            if request.GET.get('household_structure'):
                kwargs["queryset"] = HouseholdStructure.objects.filter(
                    id__exact=request.GET.get('household_structure', 0))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
