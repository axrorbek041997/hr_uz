from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

class PaymeCardForm(forms.Form):
    card_number = forms.CharField(label='Karta raqami ', max_length=16, min_length=16, widget=forms.TextInput(attrs={'placeholder': '8600123456789012'}))
    expire = forms.CharField(label='Amal qilish muddati ', min_length=4, max_length=4, widget=forms.TextInput(attrs={'placeholder': 'MMYY'}))

class PaymeVerifyForm(forms.Form):
    code = forms.IntegerField(label='Tasdiqlash kodi', widget=forms.TextInput(attrs={'placeholder': '123456'}))