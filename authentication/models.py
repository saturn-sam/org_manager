from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.conf import settings

from django.utils.timezone import now


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,  **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('Email Address'), unique=True)
    first_name = models.CharField(_('First Name'), max_length=150, blank=False)
    last_name = models.CharField(_('Last Name'), max_length=150, blank=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    readonly_fields = ('email',)
    

    objects = CustomUserManager()



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,default='user')
    member_id = models.IntegerField(default=0,blank=True)
    signup_confirmation = models.BooleanField(default=False)
    disable_status = models.BooleanField(default=False)
    image = models.ImageField(_("Member's Image"), default='profile_pic/defaultpp.jpg', upload_to='profile_pic')
    date_of_appointment = models.DateField(_("Member's Image (YYYY-MM-DD)"), default=now, blank=True)
    father_or_husband_name = models.CharField(_("Father/Husband's Name"), default='NULL', max_length=150, blank=False)
    mother_name = models.CharField(_("mother's Name"), default='NULL', max_length=150, blank=False)
    per_vill = models.CharField(_("Village(Permanent)"), default='NULL', max_length=250, blank=False)
    per_po = models.CharField(_("Post Office(Permanent)"), default='NULL', max_length=250, blank=False)
    per_ps = models.CharField(_("Thana(Permanent)"), default='NULL', max_length=250, blank=False)
    per_dist = models.CharField(_("District(Permanent)"), default='NULL', max_length=250, blank=False)
    pre_vill = models.CharField(_("Village(Present)"), default='NULL', max_length=250, blank=False)
    pre_po = models.CharField(_("Post Office(Present)"), default='NULL', max_length=250, blank=False)
    pre_ps = models.CharField(_("Thana(Present)"), default='NULL', max_length=250, blank=False)
    pre_dist = models.CharField(_("District(Present)"), default='NULL', max_length=250, blank=False)
    dob = models.DateField(_("Date of Birth (YYYY-MM-DD)"), default=now, blank=False)
    phone = models.CharField(_("Phone No."), default='NULL', max_length=250, blank=False)
    blood_group = models.CharField(_("Blood Group"), max_length=50, blank=True)
    nid = models.CharField(_("NID No."), default='NULL', max_length=50, blank=False)
    passport = models.CharField(_("Passport No"), max_length=50, blank=True)
    tin = models.CharField(_("TIN"), max_length=50, blank=True)
    driving_license = models.CharField(_("Driving License"), max_length=50, blank=True)
    profession = models.CharField(_("Profession"), default='NULL', max_length=50, blank=False)
    religion = models.CharField(_("Religion"), default='NULL', max_length=50, blank=False)
    nominee_image = models.ImageField(_("Image of nominee"), default='profile_pic/defaultpp.jpg', upload_to='profile_pic')
    nominee_name = models.CharField(_("Name of Nominee"), default='NULL', max_length=250, blank=False)
    nominee_father_or_husband_name = models.CharField(_("Father/Husband's Name of Nominee"), default='NULL', max_length=250, blank=False)
    nominee_mother_name = models.CharField(_("Mother's Name of Nominee"), default='NULL', max_length=250, blank=False)
    nominee_per_vill = models.CharField(_("Village of Nominee(Permanent)"), default='NULL', max_length=250, blank=False)
    nominee_per_po = models.CharField(_("Post Office of Nominee(Permanent)"), default='NULL', max_length=250, blank=False)
    nominee_per_ps = models.CharField(_("Thana of Nominee(Permanent)"), default='NULL', max_length=250, blank=False)
    nominee_per_dist = models.CharField(_("District of Nominee(Permanent)"), default='NULL', max_length=250, blank=False)
    nominee_pre_vill = models.CharField(_("Village of Nominee(Present)"), default='NULL', max_length=250, blank=False)
    nominee_pre_po = models.CharField(_("Post Office of Nominee(Present)"), default='NULL', max_length=250, blank=False)
    nominee_pre_ps = models.CharField(_("Thana of Nominee(Present)"), default='NULL', max_length=250, blank=False)
    nominee_pre_dist = models.CharField(_("District of Nominee(Present)"), default='NULL', max_length=250, blank=False)

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)    

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


