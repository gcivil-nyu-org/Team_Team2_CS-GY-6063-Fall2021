from django.contrib import admin
from .models import Restroom, Rating, ClaimedRestroom

admin.site.register(Restroom)
admin.site.register(Rating)
admin.site.register(ClaimedRestroom)
