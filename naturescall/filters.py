import django_filters
from .models import Restroom
from django_filters.widgets import BooleanWidget


class RestroomFilter(django_filters.FilterSet):
    accessible = django_filters.BooleanFilter(
        field_name="accessible", widget=BooleanWidget()
    )
    family_friendly = django_filters.BooleanFilter(
        field_name="family_friendly", widget=BooleanWidget()
    )
    transaction_not_required = django_filters.BooleanFilter(
        field_name="transaction_not_required", widget=BooleanWidget()
    )

    class Meta:
        model = Restroom
        fields = ("accessible", "family_friendly", "transaction_not_required")
