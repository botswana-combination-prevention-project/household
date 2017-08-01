from ..constants import ELIGIBLE_REPRESENTATIVE_ABSENT, NO_HOUSEHOLD_INFORMANT
from ..constants import REFUSED_ENUMERATION, SEASONALLY_NEARLY_ALWAYS_OCCUPIED
from ..constants import UNKNOWN_OCCUPIED


def is_failed_enumeration_attempt_household_status(household_status):
    return household_status in [
        ELIGIBLE_REPRESENTATIVE_ABSENT,
        NO_HOUSEHOLD_INFORMANT,
        REFUSED_ENUMERATION]


def is_failed_enumeration_attempt(obj, attrname=None):
    attrname = attrname or 'household_status'
    return is_failed_enumeration_attempt_household_status(getattr(obj, attrname))


def is_no_informant(obj, attrname=None):
    attrname = attrname or 'eligibles_last_seen_home'
    return getattr(obj, attrname) in [SEASONALLY_NEARLY_ALWAYS_OCCUPIED, UNKNOWN_OCCUPIED]
