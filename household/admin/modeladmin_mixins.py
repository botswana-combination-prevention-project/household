from django.apps import apps as django_apps
from django.contrib import admin
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_base.modeladmin_mixins import (
    ModelAdminNextUrlRedirectMixin, ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin, ModelAdminAuditFieldsMixin, ModelAdminReadOnlyMixin)

from ..models import HouseholdStructure, Household, HouseholdLog


class ModelAdminMixin(ModelAdminNextUrlRedirectMixin, ModelAdminFormInstructionsMixin,
                      ModelAdminFormAutoNumberMixin, ModelAdminRevisionMixin,
                      ModelAdminAuditFieldsMixin, ModelAdminReadOnlyMixin,
                      admin.ModelAdmin):

    list_per_page = 10
    date_hierarchy = 'modified'
    empty_value_display = '-'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "plot":
            Plot = django_apps.get_model(*'plot.plot'.split('.'))
            if request.GET.get('plot'):
                kwargs["queryset"] = Plot.objects.filter(
                    id__exact=request.GET.get('plot', 0))
        if db_field.name == "household":
            if request.GET.get('household'):
                kwargs["queryset"] = Household.objects.filter(
                    id__exact=request.GET.get('household', 0))
        if db_field.name == "household_log":
            if request.GET.get('household_log'):
                kwargs["queryset"] = HouseholdLog.objects.filter(
                    id__exact=request.GET.get('household_log', 0))
        if db_field.name == "household_structure":
            if request.GET.get('household_structure'):
                kwargs["queryset"] = HouseholdStructure.objects.filter(
                    id__exact=request.GET.get('household_structure', 0))
        return super(ModelAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def view_on_site(self, obj):
        try:
            household_structure = obj.household_log.household_structure
        except AttributeError:
            try:
                household_identifier = obj.household.household_identifier
            except AttributeError:
                household_identifier = obj.household_identifier
            listboard_url_name = django_apps.get_app_config(
                'household_dashboard').listboard_url_name
            try:
                return reverse(
                    listboard_url_name, kwargs=dict(household_identifier=household_identifier))
            except NoReverseMatch:
                return super().view_on_site(obj)
        else:
            listboard_url_name = django_apps.get_app_config(
                'enumeration').listboard_url_name
            try:
                return reverse(
                    listboard_url_name, kwargs=dict(
                        household_structure=str(household_structure.id),
                        survey_schedule=household_structure.survey_schedule))
            except NoReverseMatch:
                return super().view_on_site(obj)
