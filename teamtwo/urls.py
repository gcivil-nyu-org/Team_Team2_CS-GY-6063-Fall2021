"""teamtwo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from accounts.forms import EmailValidationOnForgotPassword
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", include("naturescall.urls", namespace="naturescall")),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(
            form_class=EmailValidationOnForgotPassword
        ),
        name="password_reset",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    path("qr_code/", include("qr_code.urls", namespace="qr_code")),
]
