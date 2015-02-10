from django.db import models

from organizations.models import Organization
from users.models import OrgaUser

# Create your models here.
class HostedProject(models.Model):
    name = models.CharField(max_length=15)
    
    plugItURI = models.URLField()
    plugItCustomUrlKey = models.CharField(max_length=10, blank=True, null=True)
    
    plugItOrgaMode = models.BooleanField(default=True)
    plugItProxyMode = models.BooleanField(default=False)
    
    plugItLimitOrgaJoinable = models.ForeignKey(Organization, blank=True, null=True)
    plugItApiKey = models.CharField(max_length=10, blank=True, null=True)
    
    read_members = models.ManyToManyField(OrgaUser, null=True, related_name='read_hostedprojects')
    write_members = models.ManyToManyField(OrgaUser, null=True, related_name='write_hostedprojects')

    TEMPLATE_CHOICES = (
                        ('rd','radiodns.html'),
                        )
    plugItTemplate = models.CharField(max_length=2, choices=TEMPLATE_CHOICES)
    
    def isMemberRead(self, user):
        return user in self.read_members.all()
    
    def isMemberWrite(self, user):
        return user in self.write_members.all()
