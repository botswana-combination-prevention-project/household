from django.test import TestCase, tag

from edc_sync.test_mixins import SyncTestSerializerMixin

from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag('review', 'slow')
class TestNaturalKey(SyncTestSerializerMixin, TestCase):

    def test_natural_key_attrs(self):
        self.sync_test_natural_key_attr('household')

    def test_get_by_natural_key_attr(self):
        self.sync_test_get_by_natural_key_attr('household')
