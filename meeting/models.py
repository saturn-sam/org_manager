from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

# Create your models here.

# class MeetingType(models.Model):
#     name = models.CharField(_("Meeting Type"), max_length=50)
    
#     class Meta:
#         verbose_name = _("MeetingType")
#         verbose_name_plural = _("MeetingTypes")

#     def __str__(self):
#         return self.name

class Meeting(models.Model):
    MEETING_TYPE_CHOICE = (
        ('Monthly Meeting', 'Monthly Meeting'),
        ('Annual General Meeting', 'Annual General Meeting'),
        ('Special Meeting', 'Special Meeting'),
    )
    number = models.IntegerField(_("Meeting Number"), default=0, blank=False, primary_key = True)
    date = models.DateTimeField(_("Meeting Date"), auto_now=False, auto_now_add=False)
    chair = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Meeting Chair"), related_name='chair', on_delete=models.CASCADE)
    place = models.CharField(max_length=250, default="NULL", blank=False, )
    mtype = models.CharField(_("Meeting Type"), max_length=100, choices=MEETING_TYPE_CHOICE, blank=False, null=False)
    minute_taker = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Minutes Taker"), related_name='minute_taker', on_delete=models.CASCADE)
    final_approval = models.BooleanField(_("Final Approval"), default=0)

    def __int__(self):
        return str(self.number)


class Agenda(models.Model):
    meeting_number = models.ForeignKey(Meeting, blank=False, verbose_name=_("Meeting ID"), on_delete=models.CASCADE)
    topic = models.CharField(_("Discussion Topic"), max_length=250, default="NULL", blank=False)
    topic_initiator =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Agenda Topic Initiator"), related_name='topic_initiator', on_delete=models.CASCADE)
    discussion = models.TextField(_("Topic Discussion"), blank=True)
    action = models.CharField(_("Action on This Matter"), max_length=250, default="NULL", blank=False)
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Responsible Preson to execute this action"), related_name='responsible_person', on_delete=models.CASCADE)
    deadline = models.DateTimeField(_("Action Execution Deadline"), auto_now=False, auto_now_add=False)
    response_from_responsible_person = models.TextField(_("Response"), blank=True)
    response_date = models.DateTimeField(null=True, blank=True)

    

    class Meta:
        verbose_name = _("Agenda")
        verbose_name_plural = _("Agendas")

    def __str__(self):
        return self.topic

class Attendance(models.Model):
    meeting_number = models.ForeignKey(Meeting, blank=False, verbose_name=_("Meeting ID"), on_delete=models.CASCADE)
    attendee = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Attendee"), related_name='attendee', on_delete=models.CASCADE,  null=True)

    

    class Meta:
        verbose_name = _("Attendance")
        verbose_name_plural = _("Attendances")

    def __int__(self):
        return self.attendee


