from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from .models import Profile

# Create your tests here.


class ProfileTests(TestCase):
    def test_profile_normal_access(self):
        """
        Once a user is logged in, the profile page should be accessible
        """
        user = User.objects.create_user("Howard", "howard@gmail.com")
        self.client.force_login(user=user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)

    def test_post_profile(self):
        """
        A user goes to the profile page and is able to update the user
        information
        """
        user = User.objects.create_user("Howard", "howard@gmail.com")
        self.client.force_login(user=user)
        response = self.client.post(
            reverse("accounts:profile"),
            data={
                "email": "Hao@gmail.com",
                "profilename": "Howard",
                "accessible": "True",
                "family_friendly": "False",
                "transaction_not_required": "False",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.all()[0].email, "Hao@gmail.com")
        self.assertEqual(Profile.objects.all()[0].accessible, True)
        self.assertEqual(Profile.objects.all()[0].family_friendly, False)
        self.assertEqual(Profile.objects.all()[0].transaction_not_required, False)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(messages[0], "Your account has been updated!")
