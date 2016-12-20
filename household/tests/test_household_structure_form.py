from django.test import TestCase

from .test_mixins import HouseholdMixin


class TestHouseholdStructureForm(HouseholdMixin, TestCase):

    def setUp(self):
        super(TestHouseholdStructureForm, self).setUp()
        self.make_household_with_household_log_entry()
        self.options = {}

    def test_enumerations_attemptsyes(self):
        self.options.update()
        infant_birth_exam = InfantBirthExamForm(data=self.options)
        errors = ''.join(infant_birth_exam.errors.get('__all__'))
        self.assertIn(u'If abnormal, please specify.', errors)
