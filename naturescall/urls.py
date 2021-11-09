from django.urls import path, include

# from django.contrib.auth import views as auth_views
from . import views

app_name = "naturescall"
urlpatterns = [
    path("", views.index, name="index"),
    path("search_restroom/", views.search_restroom, name="search_restroom"),
    path("restroom_detail/<int:r_id>", views.restroom_detail, name="restroom_detail"),
    path("add_restroom/<slug:r_id>", views.add_restroom, name="add_restroom"),
    path("filter_restroom/", views.filter_restroom, name="filter_restroom"),
    path("rate_restroom/<int:r_id>", views.rate_restroom, name="rate_restroom"),
]
urlpatterns += [
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("accounts/", include("django.contrib.auth.urls")),
]
