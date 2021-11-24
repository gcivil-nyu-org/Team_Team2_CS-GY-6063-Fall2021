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
    # last_modified = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    accessible = models.BooleanField(default=False)
    family_friendly = models.BooleanField(default=False)
    transaction_not_required = models.BooleanField(default=False)
    title = models.CharField(blank=False, max_length=255, default="Restroom")

    def __str__(self):
        return f"{self.title[:50]}..."


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


class ClaimedRestroom(models.Model):
    """Class to hold claimed restrooms and associated
    information"""

    restroom_id = models.ForeignKey(Restroom, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{Restroom.objects.get(id=self.restroom_id_id).title[:50]}..."


class Coupon(models.Model):
    """Class to hold coupons for claimed restrooms"""

    cr_id = models.ForeignKey(ClaimedRestroom, on_delete=models.CASCADE)
    description = models.TextField(blank=False, null=False)


class Transaction(models.Model):
    """Class to hold transactions"""

    coupon_id = models.ForeignKey(Coupon, on_delete=models.RESTRICT)
    user_id = models.ForeignKey(User, on_delete=models.RESTRICT)
    timestamp = models.DateTimeField(auto_now_add=True)
