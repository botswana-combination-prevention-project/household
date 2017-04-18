from django.apps import apps as django_apps

from edc_map.site_mappers import site_mappers

from ..models import HouseholdStructure
from .wrappers import HouseholdStructureModelWrapper


class HouseholdStructureViewMixin:

    household_structure_model_wrapper_class = HouseholdStructureModelWrapper

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._household_structure = None
        self.survey_schedules_enumerated = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for household_structure in self.household_structures:
            if household_structure.enumerated:
                self.survey_schedules_enumerated.append(
                    household_structure.survey_schedule_object)
        context.update(
            household_structure=self.household_structure_wrapped,
            household_structures=self.household_structures,
            survey_schedules_enumerated=self.survey_schedules_enumerated)
        return context

    @property
    def household_structure(self):
        """Returns a household structure model instance or None.
        """
        if not self._household_structure:
            survey_schedule = self.survey_schedule_object.field_value
            edc_device_app_config = django_apps.get_app_config('edc_device')
            if edc_device_app_config.is_central_server:
                survey_schedule = self.survey_schedule_object.field_value.replace(site_mappers.current_map_area, '')
            try:
                self._household_structure = HouseholdStructure.objects.get(
                    household=self.household,
                    survey_schedule__icontains=survey_schedule)
            except HouseholdStructure.DoesNotExist:
                self._household_structure = None
        return self._household_structure

    @property
    def household_structure_wrapped(self):
        """Returns a wrapped household structure.
        """
        return self.household_structure_model_wrapper_class(
            self.household_structure)

    @property
    def household_structures(self):
        """Returns a Queryset.
        """
        return HouseholdStructure.objects.filter(
            household=self.household).order_by('survey_schedule')
