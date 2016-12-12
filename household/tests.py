from django.test import TestCase

from .models import Household


class TestHousehold(TestCase):

    def test_create(self):
        Household.objects.create()
