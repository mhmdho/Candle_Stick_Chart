from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


# Create your models here.


class CustomUser(AbstractUser):
    """
    Customize django user and add phone & is_phone_verified to it.
    """
    username = ''
    
    email = models.EmailField(_('email address'), unique=True)
    
    phone_regex = RegexValidator(regex=r'^09\d{9}$', message="Phone number must be entered in the format: '09121234567'.")
    phone = models.CharField(validators=[phone_regex], max_length=11, unique=True) # validators should be a list
    
    last_login = models.DateTimeField(auto_now=True)

    is_phone_verified = models.BooleanField(
        _('phone status'),
        default=False,
        help_text=_('Designates whether the phone verified.'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return self.email
