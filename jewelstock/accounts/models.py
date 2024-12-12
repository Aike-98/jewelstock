from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator

from django.utils import timezone

from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail

import uuid

#ここ( https://github.com/django/django/blob/main/django/contrib/auth/models.py )から流用
class CustomUser(AbstractBaseUser, PermissionsMixin):

    # 主キーはUUIDとする。
    id          = models.UUIDField( default=uuid.uuid4, primary_key=True, editable=False )

    username_validator  = UnicodeUsernameValidator()
    username    = models.CharField(
                    _('username'),
                    max_length=150,
                    help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
                    validators=[username_validator],
                )

    # メールアドレスは入力必須でユニークとする
    email       = models.EmailField(
                    _('email address'),
                    unique=True, 
                    error_messages={
                        'unique': _("A user with that email already exists."),
                    },)
    
    email_verified = models.BooleanField(verbose_name="メール認証済みか", default=False)

    is_staff    = models.BooleanField(
                    _('staff status'),
                    default=False,
                    help_text=_('Designates whether the user can log into this admin site.'),
                )

    is_active   = models.BooleanField(
                    _('active'),
                    default=True,
                    help_text=_(
                        'Designates whether this user should be treated as active. '
                        'Unselect this instead of deleting accounts.'
                    ),
                )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects     = UserManager()

    EMAIL_FIELD = 'email'

    # メールアドレスを使ってログインさせる。(管理ユーザーも)
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [ "username" ]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.username
