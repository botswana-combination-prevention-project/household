import arrow

from django.utils.timezone import get_current_timezone_name

from ..exceptions import HouseholdLogRequired
from ..constants import (
    ELIGIBLE_REPRESENTATIVE_ABSENT, NO_HOUSEHOLD_INFORMANT, REFUSED_ENUMERATION,
    UNKNOWN_OCCUPIED, SEASONALLY_NEARLY_ALWAYS_OCCUPIED)

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
    """Raises an exception if date part of report_datetime does not match
    a household log entry."""
    rdate = arrow.Arrow.fromdatetime(
        report_datetime, report_datetime.tzinfo).to('utc')
    household_log_entries = household_structure.householdlog.householdlogentry_set.filter(
        report_datetime__date=rdate.date()).order_by('report_datetime')
    # no entries, so raise
    if not household_log_entries:
        raise HouseholdLogRequired(
            'A \'{}\' does not exist for report date {}.'.format(
                HouseholdLogEntry._meta.verbose_name, rdate.to(
                    get_current_timezone_name()).datetime.strftime('%Y-%m-%d')))
    # some entries, raise if all are failed attempts
    household_log_entries = [obj for obj in household_log_entries if not is_failed_enumeration_attempt(obj)]
    if not household_log_entries:
        raise HouseholdLogRequired(
            '\'{}\'s exist for report date {} but all are failed enumeration attempt.'.format(
                HouseholdLogEntry._meta.verbose_name,
                rdate.to(get_current_timezone_name()).datetime.strftime('%Y-%m-%d')))
    return household_log_entries
