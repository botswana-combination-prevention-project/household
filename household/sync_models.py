from edc_sync.site_sync_models import site_sync_models
from edc_sync.sync_model import SyncModel

sync_models = [
    'household.household',
    'household.householdstructure',
    'household.householdlog',
    'household.householdassessment',
    'household.householdlogentry',
    'household.householdrefusal',
    'household.householdrefusalhistory',
    'household.householdworklist',
]

site_sync_models.register(sync_models, SyncModel)
