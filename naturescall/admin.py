from django.contrib import admin
from .models import Restroom, Rating, ClaimedRestroom, Transaction, Coupon

admin.site.register(Restroom)
admin.site.register(Rating)
admin.site.register(ClaimedRestroom)
admin.site.register(Transaction)
admin.site.register(Coupon)
