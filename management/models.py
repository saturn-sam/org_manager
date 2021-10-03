from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

class Announcement(models.Model):
    import datetime
    announcement_subject = models.CharField(_("Subject"), max_length=250, blank=False)
    announcement = models.TextField(_("Announcement"), blank=False)
    announcer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    announce_dismiss_date = models.DateTimeField(_("Announcement Expire Date"),blank=False)
    announcement_add_date = models.DateTimeField(_("Announcement Add Date"),auto_now_add=True,blank=True, null=True)
    unpublish_status = models.BooleanField(default=False,null=False)
    unpublish_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="unpublish_by_user", on_delete=models.CASCADE, blank=True, null=True)
    unpublish_date = models.DateTimeField(auto_now_add=False,blank=True, null=True)

    def __int__(self):
        return self.id