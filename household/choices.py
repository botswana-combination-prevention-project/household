from edc_constants.constants import OTHER

from household.constants import (
    ELIGIBLE_REPRESENTATIVE_PRESENT, ELIGIBLE_REPRESENTATIVE_ABSENT, NO_HOUSEHOLD_INFORMANT,
    REFUSED_ENUMERATION, SEASONALLY_NEARLY_ALWAYS_OCCUPIED, RARELY_NEVER_OCCUPIED, UNKNOWN_OCCUPIED)

NEXT_APPOINTMENT_SOURCE = (
    ('neighbour', 'Neighbour'),
    ('household member', 'Household Member'),
    ('hbc', 'Field RA'), (OTHER, 'Other')
)


HOUSEHOLD_LOG_STATUS = (
    (ELIGIBLE_REPRESENTATIVE_PRESENT, 'Eligible Representative Present'),
    (ELIGIBLE_REPRESENTATIVE_ABSENT, 'Eligible Representative Absent'),
    (NO_HOUSEHOLD_INFORMANT, 'No Household Informant'),
    (REFUSED_ENUMERATION, 'Refused Enumeration'),
)


RESIDENT_LAST_SEEN = (
    (SEASONALLY_NEARLY_ALWAYS_OCCUPIED, (
        'spent at least 4 weeks in household over the course of the past year')
     ),  # replace
    (RARELY_NEVER_OCCUPIED, 'pent less than 4 weeks in the household  over the course of the'
     'past year, or never occupied over the course of the past year'),  # NOT replaced
    (UNKNOWN_OCCUPIED, 'Don\'t know'),  # replaced
)


HOUSEHOLD_REFUSAL = (
    ('not_interested', 'Not Interested'),
    ('does_not_have_time', 'Does not have time'),
    ('DWTA', 'Don\'t want to answer'),
    ('OTHER', 'Other'),
)
