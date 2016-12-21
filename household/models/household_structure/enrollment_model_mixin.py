from django.db import models


class EnrollmentModelMixin(models.Model):

    enrolled = models.BooleanField(
        default=False,
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

    class Meta:
        abstract = True
