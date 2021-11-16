from django.shortcuts import render
from django.http import HttpResponseRedirect
from naturescall.models import Rating, ClaimedRestroom

# from django.contrib.auth import login, authenticate
from .forms import SignupForm
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from .forms import ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required


# Create your views here.
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = "Activate your Naturescall app account."
            message = render_to_string(
                "accounts/acc_active_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            to_email = form.cleaned_data.get("email")
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            messages.success(
                request,
                "Please confirm your email address to complete the registration.",
            )
            return HttpResponseRedirect(reverse("naturescall:index"))
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
            return render(request, "accounts/signup.html", {"form": form})
    else:
        form = SignupForm()
        return render(request, "accounts/signup.html", {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # login(request, user)
        messages.success(
            request,
            "Thank you for your email confirmation. Now you can login to your account.",
        )
        return HttpResponseRedirect(reverse("naturescall:index"))
    else:
        messages.error(request, "Activation link is invalid!")
        return HttpResponseRedirect(reverse("naturescall:index"))


@login_required
def view_profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            msg = "Your account has been updated!"
            messages.success(request, f"{msg}")
            return HttpResponseRedirect(reverse("naturescall:index"))
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(
            instance=request.user.profile,
            initial={"profilename": request.user.username},
        )
    current_user = request.user
    ratings = Rating.objects.filter(user_id=current_user)
    claims = ClaimedRestroom.objects.filter(user_id=current_user, verified=True)
    context = {"u_form": u_form, "p_form": p_form, "ratings": ratings, "claims": claims}
    return render(request, "accounts/profile.html", context)


# @login_required
# def edit_rating(request, r_id):
#     # security check
#     querySet = Rating.objects.filter(id=r_id)
#     if not querySet:
#         raise Http404("Sorry, the rating does not exist")
#     rating_entry = querySet[0]
#     if rating_entry.user_id != request.user:
#         raise Http404("Sorry, you do not have the right to edit this rating")
#     if request.method == "POST":
#         form = EditRating(data=request.POST)
#         if form.is_valid():
#             rating_entry = Rating.objects.get(id=r_id)
#             rating_entry.rating = form.instance.rating
#             rating_entry.headline = form.instance.headline
#             rating_entry.comment = form.instance.comment
#             rating_entry.save()
#             msg = "Your rating has been updated!"
#             messages.success(request, f"{msg}")
#             return HttpResponseRedirect(reverse("naturescall:index"))
#     else:
#         form = EditRating()
#         context = {"ratingID": r_id, "form": form, "title": rating_entry.restroom_id}
#         return render(request, "accounts/edit_rating.html", context)


# @login_required
# def delete_rating(request, r_id):
#     # security check
#     querySet = Rating.objects.filter(id=r_id)
#     if not querySet:
#         raise Http404("Sorry, the rating does not exist")
#     rating_entry = querySet[0]
#     if rating_entry.user_id != request.user:
#         raise Http404("Sorry, you do not have the right to delete this rating")
#     rating_entry.delete()
#     msg = "Your rating has been deleted!"
#     messages.success(request, f"{msg}")
#     return HttpResponseRedirect(reverse("naturescall:index"))
