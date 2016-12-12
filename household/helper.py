from .models import Household


class Helper:

    def create_household(self, count, instance=None, using=None):
        instance = instance or self
        using = using or 'default'
        if instance.pk:
            while count > 0:
                Household.objects.create(**{
                    'plot': instance,
                    'gps_target_lat': instance.gps_target_lat,
                    'gps_target_lon': instance.gps_target_lon,
                    'gps_lat': instance.gps_lat,
                    'gps_lon': instance.gps_lon,
                    'gps_degrees_e': instance.gps_degrees_e,
                    'gps_degrees_s': instance.gps_degrees_s,
                    'gps_minutes_e': instance.gps_minutes_e,
                    'gps_minutes_s': instance.gps_minutes_s})
                count -= 1

