from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Restroom(models.Model):
    """Class to hold restroom entries, including their
    yelp ID, description, and amenities."""

    # Set yelp_id max length to 100 based on this:
    # https://github.com/Yelp/yelp-fusion/issues/183
    yelp_id = models.CharField(max_length=100)
    description = models.TextField(blank=False, null=False)
    last_modified = models.DateTimeField(auto_now_add=True)
    accessible = models.BooleanField(default=False)
    family_friendly = models.BooleanField(default=False)
    transaction_not_required = models.BooleanField(default=False)
    title = models.CharField(blank=False, max_length=255, default="Restroom")


class Rating(models.Model):
    """Class to hold user-generated ratings, headlines, and comments
    for a given restroom"""

    restroom_id = models.ForeignKey(Restroom, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    headline = models.TextField(max_length=65)
    comment = models.TextField(max_length=500)
