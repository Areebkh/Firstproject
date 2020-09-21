from django import forms
from .models import CheckoutDetail

class CheckoutDetailsForm(forms.ModelForm):
    address = forms.CharField(label='Address',
                             widget=forms.TextInput(attrs={
                                 'placeholder': '123 Main St.',
                                 'class': 'form-control'
                             }))
    phone = forms.CharField(label='phone',
                              widget=forms.TextInput(attrs={
                                  'placeholder': 'Contact Number',
                                  'class': 'form-control'
                              }))
    country = forms.CharField(label='Country',
                            widget=forms.TextInput(attrs={
                                'placeholder': 'Enter a valid country',
                                'class': 'form-control'
                            }))
    state = forms.CharField(label='State',
                              widget=forms.TextInput(attrs={
                                  'placeholder': 'Enter a valid state',
                                  'class': 'form-control'
                              }))
    zip = forms.CharField(label='Zip',
                              widget=forms.TextInput(attrs={
                                  'placeholder': 'Enter a your zip/postal code',
                                  'class': 'form-control'
                              }))

    class Meta:
        model = CheckoutDetail
        fields = [
            'address',
            'phone',
            'country',
            'state',
            'zip',
        ]