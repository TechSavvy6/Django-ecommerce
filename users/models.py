from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()

User._meta.get_field('email')._unique = True
User._meta.get_field('email').blank = False
User._meta.get_field('email').null = False


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="shopaza/profile_pictures",
                              default="media/shopaza/profile_pictures/avatar.png")
    phone_no = PhoneNumberField()
    stripe_customer_id = models.CharField(
        max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")

    def __str__(self):
        return self.user.username


class Address(models.Model):
    user = models.ForeignKey(
        User, related_name='address', on_delete=models.CASCADE)
    street_address = models.CharField(_("Street Address"), max_length=100)
    postal_code = models.CharField(_("Postal Code"), max_length=10)
    city = models.CharField(_("City"), max_length=100)

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresss")

    def __str__(self):
        return self.user.username
