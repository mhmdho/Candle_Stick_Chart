from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from .managers import CustomUserManager


# Create your models here.


class CustomUser(AbstractUser):
    """
    Customize django user and add phone & is_phone_verified to it.
    """
    username = ''

    email = models.EmailField(_('email address'), unique=True)
    
    phone_regex = RegexValidator(regex=r'^\+989\d{9}$', message="Phone number must be entered in the format: '09121234567'.")
    phone = models.CharField(validators=[phone_regex], max_length=13, unique=True) # validators should be a list
    
    last_login = models.DateTimeField(auto_now=True)

    is_phone_verified = models.BooleanField(
        _('phone status'),
        default=False,
        help_text=_('Designates whether the phone verified.'),
    )

    is_email_verified = models.BooleanField(
        _('email status'),
        default=False,
        help_text=_('Designates whether the email verified.'),
    )

    is_2FA_enabled = models.BooleanField(
        _('2FA status'),
        default=False,
        help_text=_('Designates whether 2FA enabled.'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
