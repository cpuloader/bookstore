from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core import validators
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **kwargs):
        if not username:
            raise ValueError('Users must have a valid username.')

        user = self.model(
            username=username, phone=kwargs.get('phone','1234567'),
            cards=kwargs.get('cards','0000')
        )
        
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **kwargs):
        user = self.create_user(username, password, **kwargs)

        user.is_admin = True
        user.save()

        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True,
      validators=[
           validators.RegexValidator(r'^[\w.@+-]+$', 'Enter a valid username.', 'invalid')
        ])
    phone = models.CharField(max_length=10,       
      validators=[
           validators.RegexValidator(r'^[0-9]+$', 'Enter a valid phone number.', 'invalid')
        ])
    cards = models.CharField(max_length=20,
        validators=[
            validators.validate_comma_separated_integer_list
        ])
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone', 'cards']
   
    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
        
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

