from django import forms
from .models import Restroom, Rating


class LocationForm(forms.Form):
    location = forms.CharField(widget=forms.TextInput, label="Search Location")


# form for displaying yelp search

# form for adding information about restroom
class AddRestroom(forms.ModelForm):
    class Meta:
        model = Restroom
        fields = [
            "yelp_id",
            "description",
            "accessible",
            "family_friendly",
            "transaction_not_required",
        ]

    def clean(self):
        super(AddRestroom, self).clean()
        text = self.cleaned_data.get("description")
        if len(text) < 10:
            self._errors["text"] = self.error_class(
                ["Description Should Contain a minimum of 10 characters"]
            )
        return self.cleaned_data


# form for rating and commenting a restroom
class AddRating(forms.ModelForm):
    class Meta:
        model = Rating
        fields = [
            "rating",
            "headline",
            "comment",
        ]
