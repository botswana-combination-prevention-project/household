from django.conf.urls import url

from edc_constants.constants import UUID_PATTERN

from plot.patterns import plot_identifier
from survey.patterns import survey_schedule

from .admin_site import household_admin
from .patterns import household_identifier
from .views import ListboardView

app_name = 'household'

urlpatterns = [
    url(r'^listboard/'
        '(?P<household_identifier>' + household_identifier + ')/'
        '(?P<survey_schedule>' + survey_schedule + ')/',
        ListboardView.as_view(), name='listboard_url'),
    url(r'^listboard/'
        '(?P<household_identifier>' + household_identifier + ')/',
        ListboardView.as_view(), name='listboard_url'),
    url(r'^listboard/'
        '(?P<plot_identifier>' + plot_identifier + ')/',
        ListboardView.as_view(), name='listboard_url'),
    url(r'^listboard/'
        '(?P<household_structure>' + UUID_PATTERN.pattern + ')/',
        ListboardView.as_view(), name='listboard_url'),
    url(r'^listboard/'
        '(?P<household>' + UUID_PATTERN.pattern + ')/',
        ListboardView.as_view(), name='listboard_url'),
    url(r'^listboard/'
        '(?P<page>\d+)/',
        ListboardView.as_view(), name='listboard_url'),
    url(r'^listboard/',
        ListboardView.as_view(), name='listboard_url'),
    url(r'^admin/', household_admin.urls),
]
