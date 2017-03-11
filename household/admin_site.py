from django.contrib.admin import AdminSite


class HouseholdAdminSite(AdminSite):
    site_title = 'Household'
    site_header = 'Household'
    index_title = 'Household'
    site_url = '/household/list/'


household_admin = HouseholdAdminSite(name='household_admin')
