from django.test import TestCase, tag
from django.apps import apps as django_apps

from edc_sync.models import OutgoingTransaction
from edc_sync.test_mixins import SyncTestSerializerMixin

from ..models import HouseholdLog
from ..sync_models import sync_models

from .test_mixins import HouseholdMixin


@tag('ts')
class TestHouseholdSerializers(SyncTestSerializerMixin, HouseholdMixin, TestCase):

    def test_deserialize_household_models(self):
        self.make_confirmed_plot(household_count=1)
        household_log = HouseholdLog.objects.all().first()
        self.make_household_log_entry(household_log)
        self.make_household_failed_enumeration_with_household_assessment()
        verbose = True
        for outgoing_transaction in OutgoingTransaction.objects.all():
            if outgoing_transaction.tx_name in sync_models:
                model_cls = django_apps.get_app_config('household').get_model(
                    outgoing_transaction.tx_name.split('.')[1])
                obj = model_cls.objects.get(pk=outgoing_transaction.tx_pk)
                self.sync_test_deserialize(obj, outgoing_transaction, verbose)
