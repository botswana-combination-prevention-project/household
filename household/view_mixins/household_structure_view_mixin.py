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
            try:
                self._household_structure = HouseholdStructure.objects.get(
                    household=self.household,
                    survey_schedule=self.survey_schedule_object.field_value)
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
