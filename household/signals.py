from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from survey import site_surveys

from .constants import REFUSED_ENUMERATION
from .exceptions import HouseholdError
from .models import (
    Household, HouseholdRefusal, HouseholdRefusalHistory, HouseholdLog,
    HouseholdLogEntry, HouseholdAssessment, HouseholdStructure,
    is_no_informant, is_failed_enumeration_attempt)


@receiver(post_save, weak=False, sender=Household,
          dispatch_uid="household_on_post_save")
def household_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Creates a household_structure for each "current"
    survey schedule for this household.
    """
    if not raw:
        if not site_surveys.current_surveys:
            raise HouseholdError(
                'Cannot create HouseholdStructures. No surveys!')
        for survey_schedule in site_surveys.get_survey_schedules(current=True):
            try:
                HouseholdStructure.objects.get(
                    household=instance,
                    survey_schedule=survey_schedule.field_value)
            except HouseholdStructure.DoesNotExist:
                HouseholdStructure.objects.create(
                    household=instance,
                    survey_schedule=survey_schedule.field_value,
                    report_datetime=instance.report_datetime)


@receiver(post_save, weak=False, sender=HouseholdStructure,
          dispatch_uid="household_structure_on_post_save")
def household_structure_on_post_save(sender, instance, raw, created, using,
                                     **kwargs):
    if not raw:
        try:
            HouseholdLog.objects.get(household_structure__pk=instance.pk)
        except HouseholdLog.DoesNotExist:
            HouseholdLog.objects.create(
                household_structure=instance,
                report_datetime=instance.report_datetime)
        if instance.enumerated:
            try:
                HouseholdAssessment.objects.get(
                    household_structure=instance).delete()
            except HouseholdAssessment.DoesNotExist:
                pass


@receiver(post_save, weak=False, sender=HouseholdLog,
          dispatch_uid="household_log_on_post_save")
def household_log_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        if instance.last_log_status != REFUSED_ENUMERATION:
            HouseholdRefusal.objects.using(using).filter(
                household_structure=instance.household_structure).delete()
        # save to update enumeration attempts
        instance.household_structure.save()


@receiver(post_save, weak=False, sender=HouseholdLogEntry,
          dispatch_uid="household_log_entry_on_post_save")
def household_log_entry_on_post_save(sender, instance, raw, created, using,
                                     **kwargs):
    if not raw:
        if created:
            household_structure = instance.household_log.household_structure
            household_structure.enumeration_attempts += 1
            if is_failed_enumeration_attempt(instance):
                household_structure.failed_enumeration_attempts += 1
            household_structure.save()


@receiver(post_delete, weak=False, sender=HouseholdLogEntry,
          dispatch_uid="household_log_entry_on_post_delete")
def household_log_entry_on_post_delete(instance, using, **kwargs):
    household_structure = instance.household_log.household_structure
    household_structure.enumeration_attempts -= 1
    if household_structure.enumeration_attempts < 0:
        household_structure.enumeration_attempts = 0
    if is_failed_enumeration_attempt(instance):
        household_structure.failed_enumeration_attempts -= 1
    if household_structure.failed_enumeration_attempts < 0:
        household_structure.failed_enumeration_attempts = 0
    household_structure.save()


@receiver(post_save, weak=False, sender=HouseholdRefusal,
          dispatch_uid="household_refusal_on_post_save")
def household_refusal_on_post_save(sender, instance, raw, created, using,
                                   **kwargs):
    if not raw:
        instance.household_structure.refused_enumeration = True
        instance.household_structure.save()


@receiver(post_delete, weak=False, sender=HouseholdRefusal,
          dispatch_uid="household_refusal_on_delete")
def household_refusal_on_delete(instance, using, **kwargs):
    # update the history model
    HouseholdRefusalHistory.objects.create(
        household_structure=instance.household_structure,
        report_datetime=instance.report_datetime,
        reason=instance.reason,
        reason_other=instance.reason_other)
    instance.household_structure.refused_enumeration = False
    instance.household_structure.save()


@receiver(post_save, weak=False, sender=HouseholdAssessment,
          dispatch_uid='household_assessment_on_post_save')
def household_assessment_on_post_save(sender, instance, raw, created, using,
                                      **kwargs):
    if not raw:
        if created:
            instance.household_structure.failed_enumeration = True
        instance.household_structure.no_informant = is_no_informant(instance)
        instance.household_structure.save()


@receiver(post_delete, weak=False, sender=HouseholdAssessment,
          dispatch_uid="household_assessment_on_delete")
def household_assessment_on_delete(sender, instance, using, **kwargs):
    instance.household_structure.failed_enumeration = False
    instance.household_structure.no_informant = False
    instance.household_structure.save()
