from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.contrib import messages
from django.contrib.auth import logout

from .forms import EditPhoneNoForm, EditProfilePictureForm, DeleteAccountForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from meta.views import Meta

User = get_user_model()


def settings(request):
    meta = Meta(title=_("Settings"), description=_("User Settings"))
    return render(request, 'users/settings.html', {"meta": meta})


class EditPhoneNoView(FormView):
    template_name = 'users/edit_phone_no.html'
    form_class = EditPhoneNoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta"] = Meta(title=_("Edit Phone No."),
                               description=_("Edit Phone No."))
        return context

    def get_initial(self):
        initial = super().get_initial()

        initial.update({'phone_no': self.request.user.profile.phone_no})
        return initial

    def form_valid(self, form):
        user = self.request.user
        user.profile.phone_no = form.cleaned_data.get('phone_no')
        user.profile.save()
        messages.success(self.request, _("Phone No. Updated"))
        return redirect('settings')


class UpdateProfilePictureView(FormView):
    template_name = 'users/update_profile_picture.html'
    form_class = EditProfilePictureForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta"] = Meta(
            title=_("Update Profile Picture"), description=_("Update Profile Picture"))
        return context

    def form_valid(self, form):  # pragma: no cover
        user = self.request.user
        user.profile.image = form.cleaned_data.get('profile_picture')
        user.profile.save()
        messages.success(self.request, _("Profice Picture Updated"))
        return redirect('settings')


@login_required
def delete_account(request):
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST)

        if form.is_valid():
            if request.POST["delete_checkbox"]:
                rem = User.objects.get(username=request.user)
                rem.delete()
                logout(request)
                messages.info(
                    request, _("Your account has been deleted."))
                return redirect("index")
    else:
        form = DeleteAccountForm()
    meta = Meta(title=_("Delete Account"), description=_(
        "Are you sure you want to delete your account?"))
    context = {'form': form, "meta": meta}
    return render(request, 'users/delete_account.html', context)
