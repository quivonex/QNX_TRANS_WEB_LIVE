from django import forms
from django.contrib.auth.forms import AuthenticationForm
from company.models import FinancialYears
from branches.models import BranchMaster


class CustomLoginForm(AuthenticationForm):
    financial_year = forms.ModelChoiceField(
        queryset=FinancialYears.objects.filter(is_active=True),
        required=True,
        empty_label="Select Financial Year"
    )
    branch = forms.ModelChoiceField(
        queryset=BranchMaster.objects.filter(is_active=True),
        required=True,
        empty_label="Select Branch ")
