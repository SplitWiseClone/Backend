from django.contrib.auth.models import User
from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = 'currency', 'taker', 'giver', 'amount', 'category', 'description',

