import arrow

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from faker import Faker

from edc_base.utils import get_utcnow
from plot.utils import get_anonymous_plot

from ..constants import ELIGIBLE_REPRESENTATIVE_ABSENT, NO_HOUSEHOLD_INFORMANT
from ..constants import REFUSED_ENUMERATION, UNKNOWN_OCCUPIED
from ..constants import SEASONALLY_NEARLY_ALWAYS_OCCUPIED, ELIGIBLE_REPRESENTATIVE_PRESENT
from ..exceptions import HouseholdLogRequired
from .household_log_entry import HouseholdLogEntry
from .household import Household
from .household_structure import HouseholdStructure


fake = Faker()


def is_failed_enumeration_attempt(obj, attrname=None):
    attrname = attrname or 'household_status'
    return is_failed_enumeration_attempt_household_status(getattr(obj, attrname))


def is_failed_enumeration_attempt_household_status(household_status):
    return household_status in [
        ELIGIBLE_REPRESENTATIVE_ABSENT,
        NO_HOUSEHOLD_INFORMANT,
        REFUSED_ENUMERATION]


def is_no_informant(obj, attrname=None):
    attrname = attrname or 'eligibles_last_seen_home'
    return getattr(obj, attrname) in [SEASONALLY_NEARLY_ALWAYS_OCCUPIED, UNKNOWN_OCCUPIED]


def get_anonymous_household_structure(survey_schedule_name):
    plot = get_anonymous_plot()
    household = Household.objects.get(plot=plot)
    return HouseholdStructure.objects.get(
        household=household,
        householdsurvey_schedule=survey_schedule_name)


def todays_log_entry_or_raise(household_structure=None,
                              report_datetime=None, **options):
    """Returns the current HouseholdLogEntry or raises a
    HouseholdLogRequired exception.

    If report_datetime is provided, use that. This means a model
    can be edited if its report_datetime matches a household log entry.

    Comparison is by date not datetime
    """

    def create_log_for_anonymous(household_structure):
        household_log_entry = HouseholdLogEntry.objects.create(
            household_log=household_structure.householdlog,
            report_datetime=get_utcnow(),
            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT,
            comment='anonymous')
        return household_log_entry

    rdate = arrow.Arrow.fromdatetime(
        report_datetime, report_datetime.tzinfo)
    # any log entries?
    anonymous_plot = get_anonymous_plot()
    if household_structure.householdlog.householdlogentry_set.all().count() == 0:
        if household_structure.household.plot == anonymous_plot:
            household_log_entry = create_log_for_anonymous(household_structure)
        else:
            raise HouseholdLogRequired(
                'No {0} records exist for \'{1}\'. \'{0}\' is required.'.format(
                    HouseholdLogEntry._meta.verbose_name.title(),
                    household_structure))
    else:
        # any log entries for given report_datetime.date?
        obj = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last()
        last_rdate = arrow.Arrow.fromdatetime(
            obj.report_datetime, obj.report_datetime.tzinfo)
        try:
            household_log_entry = household_structure.householdlog.householdlogentry_set.get(
                report_datetime__date=rdate.to('UTC').date())
        except HouseholdLogEntry.DoesNotExist:
            if household_structure.household.plot == anonymous_plot:
                household_log_entry = create_log_for_anonymous(
                    household_structure)
            else:
                try:
                    household_log_entry = household_structure.householdlog.householdlogentry_set.get(
                        report_datetime__date=get_utcnow().date())
                except HouseholdLogEntry.DoesNotExist:
                    raise HouseholdLogRequired(
                        'A \'{}\' does not exist for {}, last log '
                        'entry was on {}.'.format(
                            HouseholdLogEntry._meta.verbose_name,
                            report_datetime.strftime('%Y-%m-%d %H:%M %Z'),
                            last_rdate.to(report_datetime.tzname()).datetime.strftime(
                                '%Y-%m-%d %H:%M %Z')))
        except MultipleObjectsReturned:
            household_log_entry = household_structure.householdlog.householdlogentry_set.filter(
                report_datetime__date=rdate.to(settings.TIME_ZONE).date()).last()
    return household_log_entry
