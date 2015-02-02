# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class Organization(models.Model):
    name = models.CharField(max_length=10)
    
    def __unicode__(self):
        return u'%s' % (self.name)
    
class OrgaUser(AbstractUser):    
    organization = models.ForeignKey(Organization, null=True)
