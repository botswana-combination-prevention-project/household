import arrow

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from edc_base.utils import get_utcnow
from plot.utils import get_anonymous_plot

from ..constants import ELIGIBLE_REPRESENTATIVE_PRESENT
from ..exceptions import HouseholdLogRequired


def todays_log_entry_or_raise(household_structure=None, report_datetime=None,
                              household_log_entry_model=None, **options):
    """Returns the current Household Log Entry or raises a
    HouseholdLogRequired exception.

    If report_datetime is provided, use that. This means a model
    can be edited if its report_datetime matches a household log entry.

    Comparison is by date not datetime
    """

    def create_log_for_anonymous(household_structure, household_log_entry_model=None):
        model_cls = django_apps.get_model(household_log_entry_model)
        household_log_entry = model_cls.objects.create(
            household_log=household_structure.householdlog,
            report_datetime=get_utcnow(),
            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT,
            comment='anonymous')
        return household_log_entry

    if not household_log_entry_model:
        household_log_entry_model = 'household.householdlogentry'

    rdate = arrow.Arrow.fromdatetime(
        report_datetime, report_datetime.tzinfo)
    anonymous_plot = get_anonymous_plot()
    # any log entries?
    if household_structure.householdlog.householdlogentry_set.all().count() == 0:
        if household_structure.household.plot == anonymous_plot:
            household_log_entry = create_log_for_anonymous(
                household_structure,
                household_log_entry_model=household_log_entry_model)
        else:
            raise HouseholdLogRequired(
                f'No Household Log Entry records exist for \'{household_structure}\'. '
                'Household Log Entry is required.')
    else:
        # any log entries for given report_datetime.date?
        obj = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last()
        last_rdate = arrow.Arrow.fromdatetime(
            obj.report_datetime, obj.report_datetime.tzinfo)
        try:
            household_log_entry = household_structure.householdlog.householdlogentry_set.get(
                report_datetime__date=rdate.to('UTC').date())
        except ObjectDoesNotExist:
            if household_structure.household.plot == anonymous_plot:
                household_log_entry = create_log_for_anonymous(
                    household_structure,
                    household_log_entry_model=household_log_entry_model)

            else:
                try:
                    household_log_entry = (
                        household_structure.householdlog.householdlogentry_set.get(
                            report_datetime__date=get_utcnow().date()))
                except ObjectDoesNotExist:
                    last_report_datetime = last_rdate.to(
                        report_datetime.tzname()).datetime.strftime(
                        '%Y-%m-%d %H:%M %Z')
                    report_datetime = report_datetime.strftime(
                        '%Y-%m-%d %H:%M %Z')
                    raise HouseholdLogRequired(
                        f'A \'Household Log Entry\' does not exist for {report_datetime}, '
                        f'last log entry was on {last_report_datetime}.')
        except MultipleObjectsReturned:
            household_log_entry = household_structure.householdlog.householdlogentry_set.filter(
                report_datetime__date=rdate.to(settings.TIME_ZONE).date()).last()
    return household_log_entry
