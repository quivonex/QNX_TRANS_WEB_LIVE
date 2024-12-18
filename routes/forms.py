# routes/forms.py
from django import forms


class DistanceForm(forms.Form):
    postal_code1 = forms.CharField(label='Postal Code 1', max_length=10)
    postal_code2 = forms.CharField(label='Postal Code 2', max_length=10)
