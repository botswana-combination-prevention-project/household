from django.apps import apps as django_apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .constants import REFUSED_ENUMERATION, SEASONALLY_NEARLY_ALWAYS_OCCUPIED, UNKNOWN_OCCUPIED
from .exceptions import HouseholdError
from .models import (
    Household, HouseholdRefusal, HouseholdRefusalHistory, HouseholdLog, HouseholdLogEntry,
    HouseholdAssessment, HouseholdStructure)


@receiver(post_save, weak=False, sender=Household, dispatch_uid="household_on_post_save")
def household_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Creates a household_structure for each survey for this household."""
    if not raw:
        app_config = django_apps.get_app_config('survey')
        if not app_config.current_surveys:
            raise HouseholdError('Cannot create HouseholdStructures. No surveys!')
        for current_survey in app_config.current_surveys:
            try:
                HouseholdStructure.objects.get(
                    household=instance,
                    survey=current_survey.label)
            except HouseholdStructure.DoesNotExist:
                HouseholdStructure.objects.create(
                    household=instance,
                    survey=current_survey.label)


@receiver(post_save, weak=False, sender=HouseholdStructure, dispatch_uid="household_structure_on_post_save")
def household_structure_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        try:
            HouseholdLog.objects.get(household_structure__pk=instance.pk)
        except HouseholdLog.DoesNotExist:
            HouseholdLog.objects.create(household_structure=instance)
        if instance.enumerated and instance.no_informant:
            try:
                HouseholdAssessment.objects.get(
                    household_structure=instance).delete()
            except HouseholdAssessment.DoesNotExist:
                pass


@receiver(post_save, weak=False, sender=HouseholdLog, dispatch_uid="household_log_on_post_save")
def household_log_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        if instance.last_log_status != REFUSED_ENUMERATION:
            HouseholdRefusal.objects.using(using).filter(
                household_structure=instance.household_structure).delete()
        # save to update enumeration attempts
        instance.household_structure.save()


@receiver(post_save, weak=False, sender=HouseholdRefusal, dispatch_uid="household_refusal_on_post_save")
def household_refusal_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates household_structure refused enumeration after Household Refusal is updated."""
    if not raw:
        instance.household_structure.refused_enumeration = True
        instance.household_structure.save()


@receiver(post_delete, weak=False, sender=HouseholdRefusal, dispatch_uid="household_refusal_on_delete")
def household_refusal_on_delete(instance, using, **kwargs):
    # update the history model
    HouseholdRefusalHistory.objects.create(
        household_structure=instance.household_structure,
        report_datetime=instance.report_datetime,
        reason=instance.reason,
        reason_other=instance.reason_other)
    instance.household_structure.refused_enumeration = False
    instance.household_structure.save()


@receiver(post_save, weak=False, sender=HouseholdAssessment, dispatch_uid='household_assessment_on_post_save')
def household_assessment_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates HouseholdStructure by reseting failed_enumeration and calculating the
    if there is an informant or not based on residency."""
    if not raw:
        if created:
            instance.household_structure.failed_enumeration = True
        instance.household_structure.no_informant = instance.eligibles_last_seen_home in [
            SEASONALLY_NEARLY_ALWAYS_OCCUPIED, UNKNOWN_OCCUPIED]
        instance.household_structure.save()


@receiver(post_delete, weak=False, sender=HouseholdAssessment, dispatch_uid="household_assessment_on_delete")
def household_assessment_on_delete(sender, instance, using, **kwargs):
    instance.household_structure.no_informant = False
    instance.household_structure.save()


@receiver(post_save, weak=False, sender=HouseholdLogEntry, dispatch_uid='household_log_entry_on_post_save')
def household_log_entry_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        if not instance.household_log.last_log_datetime:
            instance.household_log.last_log_datetime = instance.report_datetime
            instance.household_log.last_log_status = instance.household_status
        elif instance.household_log.last_log_datetime <= instance.report_datetime:
            instance.household_log.last_log_datetime = instance.report_datetime
            instance.household_log.last_log_status = instance.household_status
        instance.household_log.save()
