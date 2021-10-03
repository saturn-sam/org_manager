from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
# from django.utils.timezone import make_aware

from PIL import Image
from django.conf import settings


from django.utils.timezone import now

# Create your models here.

class Subscriptionof(models.Model):
    SUBS_TYPE_CHOICE = (
        ('Monthly', 'Monthly'),
        ('Special', 'Special'),
    )
    subs_type = models.CharField(_("Subscription Type"), max_length=20, choices=SUBS_TYPE_CHOICE, blank=False, null=False)
    subs_of = models.CharField(_("Subscription (Pattern: 'January 2021')"), max_length=150, blank=False, null=False)
    insert_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    insert_date = insert_date = models.DateTimeField(auto_now_add = True)
    

    def __str__(self):
        return self.subs_of
    
    class Meta:
        ordering = ['-id', ]

class Deposite(models.Model):
    import datetime

    member_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False)
    sub_of = models.ForeignKey(Subscriptionof,  blank=False, on_delete=models.CASCADE, verbose_name = "Subscription Of")
    amount = models.IntegerField(_("Amount"), blank=False)
    bank_ref_num = models.CharField(_("Bank Reference Number"), max_length=150, blank=False)
    recipt_image = models.ImageField(_("Image of Receipt"), upload_to='receipt')
    insert_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='insert_by', blank=True, null=True)
    insert_date = models.DateTimeField(auto_now_add = True)
    delete_status = models.BooleanField(default=False)
    delete_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='delete_by',blank=True, null=True)
    delete_date = models.DateTimeField(default=timezone.make_aware(timezone.datetime(1970, 1, 1, 0, 0, 0)))
    approve_status = models.IntegerField(default=0)
    approve_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='deposit_approve_by',blank=True, null=True)
    appove_date = models.DateTimeField(default=timezone.make_aware(timezone.datetime(1970, 1, 1, 0, 0, 0)))
    receipt_id = models.IntegerField(_("Receipt Id"), blank=True, null=True)
    receipt_issue_date = models.DateTimeField(default=timezone.make_aware(timezone.datetime(1970, 1, 1, 0, 0, 0)), null=True)
    

    def __str__(self):
        return self.member_name.first_name

class ReceiptID(models.Model):
    invoice_no = models.IntegerField( null = True, blank = True)
    

    def __str__(self):
        return str(self.invoice_no)



class Earning(models.Model):
    EARNING_SOURCE_CHOICES = (
        ("Member's Deposit", "Member's Deposit"),
        ("Savings Certificate", "Savings Certificate"),
        ("FDR", "FDR"),
        ("DPS", "DPS"),
    )

    import datetime

    earning_source = models.CharField(_("Earning Source"), max_length=150, choices=EARNING_SOURCE_CHOICES, blank=False)
    description = models.CharField(_("Description of Earning"),  blank=False, max_length=250)
    amount = models.IntegerField(_("Amount"), default=0, blank=False)
    document_image = models.ImageField(_("Image of Document (If Needed)"), upload_to='receipt', null=True, blank=True)
    insert_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='earning_insert_by', blank=True, null=True)
    insert_date = models.DateTimeField(auto_now_add = False, blank=True, null=True)
    deposit_info = models.ForeignKey(Deposite, on_delete=models.CASCADE,related_name='deposit_in_earning',blank=True, null=True)
    delete_status = models.BooleanField(default=False)
    delete_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='earning_delete_by',blank=True, null=True)
    delete_date = models.DateTimeField(default=timezone.make_aware(timezone.datetime(1970, 1, 1, 0, 0, 0)))
    approve_status = models.IntegerField(default=0)
    approve_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='earning_approve_by',blank=True, null=True)
    approve_date = models.DateTimeField(_("Approved By"), default=timezone.make_aware(timezone.datetime(1970, 1, 1, 0, 0, 0)))

    def __str__(self):
        return self.earning_source



class Expenditure(models.Model):
    import datetime

    EXPENDITURE_TYPE_CHOICES = (
        ('Permanent Expenditure', 'Permanent Expenditure'),
        ('Savings', 'Savings')
    )
    EXPENDITURE_SOURCE_CHOICES = (
        ('Savings Certificate', 'Savings Certificate'),
        ('FDR', 'FDR'),
        ('Stationary', 'Stationary'),
        ('Meeting', 'Meeting'),
        ('Others', 'Others')
    )
    expenditure_source = models.CharField(_("Expenditure Source"), choices=EXPENDITURE_SOURCE_CHOICES,  blank=False, max_length=250)
    expenditure_type = models.CharField(_("Expenditure Type"), choices=EXPENDITURE_TYPE_CHOICES,  blank=False, max_length=250)
    description = models.CharField(_("Description of Expenditure"),  blank=False, max_length=250)
    amount = models.IntegerField(_("Amount"), default=0, blank=False)
    expenditure_date = models.DateField(auto_now_add = False, null=False, blank=False)
    supporting_document = models.ImageField(_("Image of Supporting Document (If Needed)"), upload_to='receipt', null=True, blank=True)
    insert_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenditure_insert_by', blank=True, null=True)
    insert_date = models.DateTimeField(auto_now_add = True)
    delete_status = models.BooleanField(default=False)
    delete_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='expenditure_earning_delete_by',blank=True, null=True)
    delete_date = models.DateTimeField(default=timezone.make_aware(timezone.datetime(1970, 1, 1, 0, 0, 0)))
    approve_status = models.IntegerField(default=0)
    approve_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='expenditure_earning_approve_by',blank=True, null=True)
    approve_date = models.DateTimeField(_("Approved By"), default=timezone.make_aware(timezone.datetime(1970, 1, 1, 0, 0, 0)))
    def __str__(self):

        return self.expenditure_source