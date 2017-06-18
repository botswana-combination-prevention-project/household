# coding=utf-8

from django.conf.urls import url

from .admin_site import household_admin

app_name = 'household'

urlpatterns = [
    url(r'^admin/', household_admin.urls),
]
