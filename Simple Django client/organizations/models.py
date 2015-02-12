from django.db import models
   
from users.models import OrgaUser
# Create your models here.

class Organization(models.Model):
    name = models.CharField(max_length=10)
    codops = models.CharField(max_length=10)

    members = models.ManyToManyField(OrgaUser, blank=True, null=True, related_name='member_organizations')
    owners = models.ManyToManyField(OrgaUser, blank=True, null=True, related_name='owner_organizations')

    def isMember(self, user):
        return user in self.members.all()
    
    def isOwner(self, user):
        return user in self.owners.all()
    
    def __unicode__(self):
        return u'%s' % (self.name)
    
