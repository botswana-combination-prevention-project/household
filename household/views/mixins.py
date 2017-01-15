from edc_base.utils import get_utcnow

from member.models.household_member.utils import todays_log_entry_or_raise

from ..exceptions import HouseholdLogRequired
from ..models import Household, HouseholdStructure

from .wrappers import HouseholdModelWrapper, HouseholdStructureModelWrapper, HouseholdLogEntryWrapper


class HouseholdViewMixin:

    household_wrapper_class = HouseholdModelWrapper

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.household = None
        self.household_identifier = None

    def get(self, request, *args, **kwargs):
        """Add household to the instance."""
        self.household_identifier = kwargs.get('household_identifier')
        try:
            household = Household.objects.get(household_identifier=self.household_identifier)
        except Household.DoesNotExist:
            self.household = None
        else:
            self.household = self.household_wrapper_class(household)
        kwargs['household'] = self.household
        return super().get(request, *args, **kwargs)


class HouseholdStructureViewMixin:

    household_structure_wrapper_class = HouseholdStructureModelWrapper

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.household_structure = None

    def get(self, request, *args, **kwargs):
        try:
            household_structure = HouseholdStructure.objects.get(
                household__id=self.household.id,  # use id, model is wrapped
                survey_schedule=self.survey_schedule_object.field_value)
        except HouseholdStructure.DoesNotExist:
            self.household_structure = None
        else:
            self.household_structure = self.household_structure_wrapper_class(household_structure)
        kwargs['household_structure'] = self.household_structure
        return super().get(request, *args, **kwargs)


class HouseholdLogEntryViewMixin:

    household_log_entry_wrapper_class = HouseholdLogEntryWrapper

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.household_log = None
        self.household_log_entry = None
        self.household_log_entries = None
        self.current_household_log_entry = None

    def get(self, request, *args, **kwargs):
        """Add household to the instance."""
        self.household_log = self.household_structure.wrapped_object.householdlog
        objs = (
            self.household_structure.wrapped_object.householdlog.householdlogentry_set.all())
        self.household_log_entries = [
            self.household_log_entry_wrapper_class(obj)
            for obj in objs.all().order_by('-report_datetime')]
        try:
            self.current_household_log_entry = todays_log_entry_or_raise(
                self.household_structure.wrapped_object, report_datetime=get_utcnow())
        except HouseholdLogRequired:
            pass
        kwargs['household_log'] = self.household_log
        kwargs['household_log_entries'] = self.household_log_entries
        kwargs['current_household_log_entry'] = self.current_household_log_entry
        return super().get(request, *args, **kwargs)
