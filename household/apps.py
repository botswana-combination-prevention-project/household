from django.apps import AppConfig as DjangoAppConfig

from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'household'

    def ready(self):
        from household.signals import household_on_post_save
