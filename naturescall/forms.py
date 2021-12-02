from django import forms
from .models import Restroom, Rating, Coupon


class LocationForm(forms.Form):
    location = forms.CharField(widget=forms.TextInput, label="Search Location")


# form for displaying yelp search

# form for adding information about restroom
class AddRestroom(forms.ModelForm):
    title = forms.CharField(
        disabled=False,
        # label="Restroom",
        # widget=forms.TextInput(attrs={"size": 80, "readonly": True}),
        widget=forms.HiddenInput(),
    )
    yelp_id = forms.SlugField(disabled=False, widget=forms.HiddenInput())
    description = forms.CharField(widget=forms.TextInput(attrs={"size": 80}))

    class Meta:
        model = Restroom
        fields = [
            "title",
            "yelp_id",
            "description",
            "accessible",
            "family_friendly",
            "transaction_not_required",
        ]


# form for rating and commenting a restroom
class AddRating(forms.ModelForm):
    headline = forms.CharField(widget=forms.TextInput(attrs={"size": 80}))
    comment = forms.CharField(widget=forms.TextInput(attrs={"size": 80}))

    class Meta:
        model = Rating
        fields = [
            "rating",
            "headline",
            "comment",
        ]


class CommentResponse(forms.ModelForm):
    response = forms.CharField(widget=forms.TextInput(attrs={"size": 80}))

    class Meta:
        model = Rating
        fields = [
            "response",
        ]


class ClaimRestroom(forms.Form):
    claim = forms.CheckboxInput()

class addCoupon(forms.ModelForm):
    description = forms.CharField(widget=forms.TextInput(attrs={"size": 80}))
    class Meta:
        model = Coupon
        fields = ["description",]
