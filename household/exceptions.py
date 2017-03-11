
class HouseholdIdentifierError(Exception):
    pass


class NotEnrolledError(Exception):
    pass


class HouseholdError(Exception):
    pass


class HouseholdLogError(Exception):
    pass


class HouseholdAlreadyEnrolledError(Exception):
    pass


class HouseholdAlreadyEnumeratedError(Exception):
    pass


class HouseholdEnumerationError(Exception):
    pass


class FormNotRequiredError(Exception):
    pass


class EnumerationAttemptsExceeded(Exception):
    pass


class HouseholdAssessmentError(Exception):
    pass


class HouseholdLogRequired(Exception):
    pass
