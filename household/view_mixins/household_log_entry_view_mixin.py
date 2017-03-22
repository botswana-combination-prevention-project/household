from edc_base.utils import get_utcnow

from member.models.household_member.utils import todays_log_entry_or_raise

from ..exceptions import HouseholdLogRequired
from ..models import HouseholdLogEntry
from .wrappers import HouseholdLogEntryModelWrapper


class HouseholdLogEntryViewMixin:

    household_log_entry_model_wrapper_class = HouseholdLogEntryModelWrapper

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_household_log_entry = None

    def get_context_data(self, **kwargs):
        """Add household log, log entry and log entries to the context.
        """
        context = super().get_context_data(**kwargs)
        context.update(
            household_log=self.household_log,
            household_log_entries=self.household_log_entries_wrapped,
            current_household_log_entry=self.current_household_log_entry_wrapped)
        return context

    @property
    def household_log(self):
        if self.household_structure:
            return self.household_structure.householdlog
        return None

    @property
    def current_household_log_entry_wrapped(self):
        """Returns a model wrapper instance.
        """
        return (
            self.household_log_entry_model_wrapper_class(
                self.current_household_log_entry
                or HouseholdLogEntry(
                    household_log=self.household_log))
        )

    @property
    def current_household_log_entry(self):
        """Returns a household log entry model instance or None.
        """
        if not self._current_household_log_entry:
            try:
                obj = todays_log_entry_or_raise(
                    self.household_structure, report_datetime=get_utcnow())
            except HouseholdLogRequired:
                obj = None
            self._current_household_log_entry = obj
        return self._current_household_log_entry

    @property
    def household_log_entries(self):
        """Returns a household_log_entry Queryset.
        """
        try:
            return (
                self.household_structure.householdlog.householdlogentry_set
                .all().order_by('-report_datetime'))
        except AttributeError as e:
            if 'householdlog' not in str(e) and 'householdlogentry_set' not in str(e):
                raise
            return HouseholdLogEntry.objects.none()

    @property
    def household_log_entries_wrapped(self):
        """Returns a list of household_log_entry model wrappers.
        """
        wrapped_objects = []
        for obj in self.household_log_entries:
            wrapped_objects.append(
                self.household_log_entry_model_wrapper_class(obj))
        return wrapped_objects
