from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class MyUser(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=30)
    permission = models.IntegerField(default=1)

    def __unicode__(self):
        return self.user.username