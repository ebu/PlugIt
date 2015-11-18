from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class OrgaUser(AbstractUser):    
    
    def getOrgas(self):
        return zip( self.member_organizations.all(), range(self.member_organizations.count()) )
