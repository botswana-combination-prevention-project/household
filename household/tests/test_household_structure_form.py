from django.test import TestCase

from .test_mixins import HouseholdMixin


class TestHouseholdStructureForm(HouseholdMixin, TestCase):

    def setUp(self):
        super(TestHouseholdStructureForm, self).setUp()
        self.make_household_with_household_log_entry()
        self.options = {}

    def test_enumerations_attempts(self):
        pass
