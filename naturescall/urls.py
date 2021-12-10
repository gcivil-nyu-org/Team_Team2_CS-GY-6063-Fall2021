from django.urls import path

# from django.contrib.auth import views as auth_views
from . import views

app_name = "naturescall"
urlpatterns = [
    path("", views.index, name="index"),
    path("about", views.about_page, name="about_page"),
    path("search_restroom/", views.search_restroom, name="search_restroom"),
    path("restroom_detail/<int:r_id>", views.restroom_detail, name="restroom_detail"),
    path("get_qr/<int:c_id>", views.get_qr, name="get_qr"),
    path("qr_confirm/<int:c_id>/<int:u_id>", views.qr_confirm, name="qr_confirm"),
    path("add_restroom/<slug:yelp_id>", views.add_restroom, name="add_restroom"),
    # path("filter_restroom/", views.filter_restroom, name="filter_restroom"),
    path("rate_restroom/<int:r_id>", views.rate_restroom, name="rate_restroom"),
    path("delete_rating/<int:r_id>", views.delete_rating, name="delete_rating"),
    path("claim_restroom/<int:r_id>", views.claim_restroom, name="claim_restroom"),
    path("manage_restroom/<int:r_id>", views.manage_restroom, name="manage_restroom"),
    path(
        "comment_responses/<int:r_id>",
        views.comment_responses,
        name="comment_responses",
    ),
    path(
        "comment_response/<int:rating_id>",
        views.comment_response,
        name="comment_response",
    ),
    path("coupon_register/<int:r_id>", views.coupon_register, name="coupon_register"),
    path("coupon_edit/<int:r_id>", views.coupon_edit, name="coupon_edit"),
    path("flag_comment/<int:rating_id>", views.flag_comment, name="flag_comment",),
    path("admin_page/", views.admin_page, name="admin_page"),
]
# urlpatterns += [
#     path("accounts/", include("accounts.urls", namespace="accounts")),
#     path("accounts/", include("django.contrib.auth.urls")),
# ]
