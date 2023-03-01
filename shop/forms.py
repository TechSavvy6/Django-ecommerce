from django import forms
from users.models import Address
from django.utils.translation import gettext_lazy as _


class CouponForm(forms.Form):
    code = forms.CharField(
        label=_('Coupon Code'), widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Coupon Code'),
        }))


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('user',)
