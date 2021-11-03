# from django.db import models
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profilename = models.CharField(default="naturescall member", max_length=50)
    accessible = models.BooleanField(default=False)
    family_friendly = models.BooleanField(default=False)
    transaction_not_required = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)


# Create your models here.
