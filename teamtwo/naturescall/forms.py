from django import forms
from .models import Restroom


class LocationForm(forms.Form):
    location= forms.CharField(widget= forms.TextInput, label= 'Search Location')

# form for displaying yelp search

# form for adding information about restroom
class AddRestroom(forms.ModelForm):
    class Meta:
        model= Restroom
        fields= ['yelp_id','Description', 'Accessible', 'FamilyFriendly', 'TransactionRequired']
    def clean(self):
        super(AddRestroom, self).clean()
        text= self.cleaned_data.get('Description')
        if len(text) <10:
            self._errors['text'] = self.error_class([
                'Description Should Contain a minimum of 10 characters'])
        return self.cleaned_data
