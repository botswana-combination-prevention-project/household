import arrow
from django.db.models import Max

from ..constants import (
    ELIGIBLE_REPRESENTATIVE_ABSENT, NO_HOUSEHOLD_INFORMANT, REFUSED_ENUMERATION,
    UNKNOWN_OCCUPIED, SEASONALLY_NEARLY_ALWAYS_OCCUPIED)
from ..exceptions import HouseholdLogRequired

from .household_log_entry import HouseholdLogEntry
from django.core.exceptions import MultipleObjectsReturned


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


def todays_log_entry_or_raise(household_structure=None, report_datetime=None):
    """Returns the current HouseholdLogEntry or raises a
    HouseholdLogRequired exception.

    Comparison is by date not datetime"""
    rdate = arrow.Arrow.fromdatetime(report_datetime, report_datetime.tzinfo)
    # any log entries?
    household_log_entry = None
    # any log entries for given report_datetime.date?
    try:
        report_datetime = HouseholdLogEntry.objects.all().aggregate(Max('report_datetime')).get('report_datetime__max')
        household_log_entry = HouseholdLogEntry.objects.get(
            household_log__household_structure=household_structure,
            report_datetime=report_datetime)
        if report_datetime.date() == rdate.date():
            return household_log_entry
    except HouseholdLogEntry.DoesNotExist:
        raise HouseholdLogRequired(
            'A \'{}\' does not exist for today, last log.'.format(
                HouseholdLogEntry._meta.verbose_name))
    except MultipleObjectsReturned:
        if report_datetime.date() == rdate.date():
            household_log_entry = HouseholdLogEntry.objects.filter(report_datetime__date=rdate.date()).order_by('report_datetime').last()
    return household_log_entry
