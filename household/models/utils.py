import arrow

from django.utils.timezone import get_current_timezone_name
from django.db.models import Max

from ..constants import (
    ELIGIBLE_REPRESENTATIVE_ABSENT, NO_HOUSEHOLD_INFORMANT, REFUSED_ENUMERATION,
    UNKNOWN_OCCUPIED, SEASONALLY_NEARLY_ALWAYS_OCCUPIED)
from ..exceptions import HouseholdLogRequired

from .household_log_entry import HouseholdLogEntry


def is_failed_enumeration_attempt(obj, attrname=None):
    attrname = attrname or 'household_status'
    return getattr(obj, attrname) in [
        ELIGIBLE_REPRESENTATIVE_ABSENT,
        NO_HOUSEHOLD_INFORMANT,
        REFUSED_ENUMERATION]


def is_no_informant(obj, attrname=None):
    attrname = attrname or 'eligibles_last_seen_home'
    return getattr(obj, attrname) in [SEASONALLY_NEARLY_ALWAYS_OCCUPIED, UNKNOWN_OCCUPIED]


def has_todays_log_entry_or_raise(household_structure, report_datetime):
    """Raises an exception if date part of report_datetime of a household log entry is not today's log."""
    rdate = arrow.Arrow.fromdatetime(
        report_datetime, report_datetime.tzinfo)
    try:
        report_datetime = HouseholdLogEntry.objects.filter(
            household_log__household_structure=household_structure).aggregate(
            Max('report_datetime')).get('report_datetime__max')
        household_log_entries = household_structure.householdlog.householdlogentry_set.all().last()
        if not report_datetime.date() == rdate.date():
            raise HouseholdLogRequired(
                'A \'{}\' does not exist for today, last log entry was on {}.'.format(
                    HouseholdLogEntry._meta.verbose_name, report_datetime.strftime('%Y-%m-%d')))
    except HouseholdLogEntry.DoesNotExist:
        raise HouseholdLogRequired(
                'A \'{}\' does not exist please add one.'.format(
                    HouseholdLogEntry._meta.verbose_name, report_datetime.strftime('%Y-%m-%d')))
    return household_log_entries
