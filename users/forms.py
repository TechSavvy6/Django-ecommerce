from django import forms
from .models import UserProfile
from phonenumber_field.formfields import PhoneNumberField

from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column


class SignupForm(forms.Form):
    phone_no = PhoneNumberField(label=_('Phone No.'), widget=forms.TextInput(
        attrs={'placeholder': _('Phone No.')}))

    def signup(self, request, user):
        user.save()
        UserProfile.objects.create(
            phone_no=self.cleaned_data.get('phone_no'),
            user=user
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-sm-6'),
                Column('email', css_class='form-group col-sm-6'),
                Column('password1', css_class='form-group col-sm-6'),
                Column('password2', css_class='form-group col-sm-6'),
                Column('phone_no', css_class='form-group col-sm-12'),
                css_class='form-row g-3'
            ),
        )


class EditPhoneNoForm(forms.Form):
    phone_no = PhoneNumberField(label=_('Phone No.'), widget=forms.TextInput(
        attrs={'placeholder': _('Phone No.')}))


class EditProfilePictureForm(forms.Form):
    profile_picture = forms.ImageField(label=_("Profice Picture"))


class DeleteAccountForm(forms.Form):
    delete_checkbox = forms.BooleanField(label=_(
        'Are you sure you want to delete your account?'), required=True)


class AddressForm(forms.Form):
    name = forms.CharField(max_length=50, label=_("Name"))
    address = forms.CharField(max_length=200, label=_("Address"))
