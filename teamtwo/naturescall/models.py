from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Restroom(models.Model):
    """Temporary class to hold fetched restroom/restaurant
    entries for their business id and rating."""
    # Set yelp_id max length to 100 based on this:
    # https://github.com/Yelp/yelp-fusion/issues/183
    yelp_id = models.CharField(max_length=100)
    rating = models.FloatField(default=0.0,
                               validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    Accessible = models.BooleanField(default=False)
    FamilyFriendly = models.BooleanField(default=False)
    TransactionRequired = models.BooleanField(default=True)
