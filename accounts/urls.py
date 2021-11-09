from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("profile", views.view_profile, name="profile"),
    path("edit_rating/<int:r_id>", views.edit_rating, name="edit_rating"),
    path("delete_rating/<int:r_id>", views.delete_rating, name="delete_rating"),
]
