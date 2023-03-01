from .views import settings, EditPhoneNoView, UpdateProfilePictureView, delete_account
from django.urls import path

urlpatterns = [
     path("settings/", settings, name="settings"),
     path("settings/delete-account", delete_account, name="delete_account"),
     path("settings/edit-phone-no/",
          EditPhoneNoView.as_view(), name="edit_phone_no"),
     path("settings/update-profile-picture/",
          UpdateProfilePictureView.as_view(), name="update_profile_picture")
]
