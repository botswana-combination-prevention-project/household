from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from edc_base.model.models import BaseUuidModel, HistoricalRecords

from survey.models import Survey

from edc_base.utils import get_utcnow
from edc_base.model.validators.date import datetime_not_future

from .household import Household


class HouseholdStructure(BaseUuidModel):

    """A system model that links a household to its household members
    for a given survey year and helps track the enrollment status, enumeration
    status, enumeration attempts and other system values. """

    household = models.ForeignKey(Household)

    survey = models.ForeignKey(Survey)

    report_datetime = models.DateField(
        verbose_name="Report date",
        default=get_utcnow,
        validators=[datetime_not_future])

    progress = models.CharField(
        verbose_name='Progress',
        max_length=25,
        default='Not Started',
        null=True,
        editable=False)

    note = models.CharField("Note", max_length=250, blank=True)

    enrolled = models.NullBooleanField(
        default=None,
        editable=False,
        help_text='enrolled by the subject consent of a household_member')

    enrolled_household_member = models.CharField(
        max_length=36,
        null=True,
        editable=False,
        help_text='pk of consenting household_member that triggered the enroll')

    enrolled_datetime = models.DateTimeField(
        null=True,
        editable=False,
        help_text='datetime household_structure enrolled')

    enumerated = models.BooleanField(
        default=False,
        editable=False,
        help_text='Set to True when first household_member is enumerated')

    enumeration_attempts = models.IntegerField(
        default=0,
        editable=False,
        help_text=('Updated by a signal on HouseholdLogEntry. '
                   'Number of attempts to enumerate a household_structure.'))

    refused_enumeration = models.BooleanField(
        default=False,
        editable=False,
        help_text='Updated by household enumeration refusal save method only')

    failed_enumeration_attempts = models.IntegerField(
        default=0,
        editable=False,
        help_text=('Updated by a signal on HouseholdLogEntry. Number of failed attempts to'
                   'enumerate a household_structure.'))

    failed_enumeration = models.BooleanField(
        default=False,
        editable=False,
        help_text='Updated by household assessment save method only')

    no_informant = models.BooleanField(
        default=False,
        editable=False,
        help_text='Updated by household assessment save method only')

    eligible_members = models.BooleanField(
        default=False,
        editable=False,
        help_text='Updated by household member save method and post_delete')

    # objects = HouseholdStructureManager()

    history = HistoricalRecords()

    def __str__(self):
        return '{} {}'.format(self.household, self.survey.survey_abbrev)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields', [])
        if not update_fields:
            if self.id and Survey.objects.current_survey().survey_slug == self.survey.survey_slug:
                Survey.objects.current_survey(report_datetime=timezone.now(), survey_slug=self.survey.survey_slug)
        super(HouseholdStructure, self).save(*args, **kwargs)

    def natural_key(self):
        return self.household.natural_key() + self.survey.natural_key()
    natural_key.dependencies = ['household.household', 'survey.survey']

    @property
    def plot(self):
        return self.household.plot.plot_identifier

    @property
    def members(self):
        return self.member_count

    @property
    def logs(self):
        HouseholdLogEntry = django_apps.get_model('household', 'HouseholdLogEntry')
        return HouseholdLogEntry.objects.filter(
            household_log__household_structure=self).count()

    @property
    def member_count(self):
        """Returns the number of household members in this household for all surveys."""
        HouseholdMember = django_apps.get_model('member', 'HouseholdMember')
        return HouseholdMember.objects.filter(household_structure__pk=self.pk).count()

    @property
    def enrolled_member_count(self):
        """Returns the number of consented (or enrolled) household members
        in this household for all surveys."""
        HouseholdMember = django_apps.get_model('member', 'HouseholdMember')
        return HouseholdMember.objects.filter(household_structure__pk=self.pk,
                                              is_consented=True).count()

    @property
    def previous(self):
        """Returns the previous household_structure (ordered by survey) relative to self
        and returns None if there is no previous survey."""
        household_structure = None
        try:
            household_structure = self.__class__.objects.filter(
                household=self.household,
                survey__datetime_start__lt=self.survey.datetime_start).exclude(
                    id=self.id).order_by('-survey__datetime_start')[0]
        except IndexError:
            pass
        return household_structure

    @property
    def first(self):
        """Returns the first household_structure (ordered by survey) using self
        and returns self if self is the first household_structure."""
        household_structure = None
        try:
            household_structure = self.__class__.objects.filter(
                household=self.household,
                survey__datetime_start__lt=self.survey.datetime_start).exclude(
                    id=self.id).order_by('survey__datetime_start')[0]
        except IndexError:
            household_structure = self
        return household_structure

    def check_eligible_representative_filled(self, using=None, exception_cls=None):
        """Raises an exception if the RepresentativeEligibility form has not been completed.

        Without RepresentativeEligibility, a HouseholdMember cannot be added."""
        exception_cls = exception_cls or ValidationError
        using = using or 'default'
        RepresentativeEligibility = django_apps.get_model('household', 'RepresentativeEligibility')
        try:
            RepresentativeEligibility.objects.using(using).get(household_structure=self)
        except RepresentativeEligibility.DoesNotExist:
            verbose_name = RepresentativeEligibility._meta.verbose_name
            raise exception_cls('\'{}\' for an eligible '
                                'representative has not been completed.'.format(verbose_name))

    @property
    def has_household_log_entry(self):
        """Confirms there is an househol_log_entry for today."""
        try:
            HouseholdLogEntry = django_apps.get_model(*'household.householdlogentry'.split('.'))
            HouseholdLogEntry.objects.filter(
                household_log=self,
                report_datetime__year=get_utcnow().year,
                report_datetime__month=get_utcnow().month,
                report_datetime__day=get_utcnow().day)
            has_household_log_entry = True
        except AttributeError:
            has_household_log_entry = False
        return has_household_log_entry

    class Meta:
        app_label = 'household'
        unique_together = ('survey', 'household')
