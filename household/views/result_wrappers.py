from plot.views import PlotResultWrapper

from ..utils import survey_from_label


class DummyHouseholdLogEntry:
    def __init__(self, household_log):
        self.household_log = household_log


class HouseholdResultWrapper(PlotResultWrapper):
    def __init__(self, obj):
        super().__init__(obj)

    def object_wrapper(self, obj):
        self.plot = obj.plot
        self.household = obj
        self.household_identifier = self.household.household_identifier

    @property
    def querystring(self):
        return [
            'next={},household_identifier'.format('household:list_url'),
            'household_identifier={}'.format(self.plot_identifier),
            'plot={}'.format(self.plot.id)]

    def log_object_urls(self, log_obj):
        log_obj.add_url = 'household:household_admin:household_householdlogentry_add'
        log_obj.change_url = 'household:household_admin:household_householdlogentry_change'
        return log_obj


class HouseholdStructureResultWrapper(HouseholdResultWrapper):
    def __init__(self, obj):
        super().__init__(obj)

    def object_wrapper(self, obj):
        self.id = obj.id
        self.plot = obj.household.plot
        self.household = obj.household
        self.household_identifier = self.household.household_identifier
        self.survey = survey_from_label(obj.survey)
        self.members = obj.householdmember_set.all()
        self.household_log = obj.householdlog
        household_log_entries = obj.householdlog.householdlogentry_set.all().order_by(
            '-report_datetime')
        self.household_log_entries = [
            self.log_object_wrapper(obj) for obj in household_log_entries]
        household_log_entry = obj.householdlog.householdlogentry_set.filter(
            report_datetime__date=obj.modified.date()).order_by('report_datetime').last()
        self.household_log_entry = self.log_object_wrapper(
            household_log_entry or DummyHouseholdLogEntry(self.household_log))

    @property
    def querystring(self):
        return [
            'next={},household_structure'.format('enumeration:list_url'),
            'household_structure={}'.format(self.id),
            'household_log={}'.format(self.household_log.id),
        ]

    def log_object_urls(self, log_obj):
        log_obj.add_url = 'household:household_admin:household_householdlogentry_add'
        log_obj.change_url = 'household:household_admin:household_householdlogentry_change'
        return log_obj
