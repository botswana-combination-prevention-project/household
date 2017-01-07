from survey.site_surveys import site_surveys
from django.core.exceptions import ImproperlyConfigured


class DummySurvey:
    survey_breadcrumbs = []
    map_area_display = None
    short_name = None


def survey_from_label(label):
    try:
        survey = site_surveys.get_survey_from_full_label(label)
        if not survey:
            raise ImproperlyConfigured(
                'Invalid survey. Survey is not registered with site_surveys. Got {}'.format(label))
    except AttributeError:
        survey = DummySurvey()
    else:
        survey.survey_breadcrumbs = [
            survey.survey_schedule.name, survey.name.upper()]
    return survey
