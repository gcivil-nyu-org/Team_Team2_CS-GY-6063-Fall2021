from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token
from django.contrib.messages import get_messages
from .models import Profile
from naturescall.models import Rating, Restroom, ClaimedRestroom

# Create your tests here.


def create_restroom(yelp_id, desc):
    """
    Create a restroom with the given parameters. Other parameters are
    left at their default values
    """
    return Restroom.objects.create(yelp_id=yelp_id, description=desc)


class ProfileTests(TestCase):
    def test_access_signup(self):
        """
        A get request to the signup page should yield a valid response
        """
        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)

    def test_account_creation_valid_form(self):
        """
        A valid form should yield a redirect upon submission and
        add a user to the database
        """
        response = self.client.post(
            reverse("accounts:signup"),
            data={
                "username": "test_user",
                "email": "test_user@email.com",
                "first_name": "test",
                "last_name": "user",
                "password1": "BDbdKDwpSt",
                "password2": "BDbdKDwpSt",
            },
        )
        all_users = User.objects.filter(id=1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(all_users), 1)

    def test_account_creation_invalid_form(self):
        """
        An invalid form should yield an error upon submission
        """
        response = self.client.post(
            reverse("accounts:signup"),
            data={
                "username": "test_user",
                "email": "test_user@email.com",
                "first_name": "test",
                "last_name": "user",
                "password1": "BDbdKDwpSt",
                "password2": "BDbdKDwpStX",
            },
        )
        self.assertContains(response, "Unsuccessful registration. Invalid information.")

    def test_user_activate_success(self):
        user = User.objects.create_user("testuser1", "howard@gmail.com")
        user.set_password("test")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        response = self.client.get(
            reverse("accounts:activate", kwargs={"uidb64": uid, "token": token})
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="testuser1")
        self.assertTrue(user.is_active)

    def test_invalid_verification_link(self):
        """
        An invalid verification request should yield a redirect
        """
        response = self.client.get(reverse("accounts:activate", args=(1, 1)))
        self.assertEqual(response.status_code, 302)

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
                "username": "How@12",
                "accessible": "True",
                "family_friendly": "False",
                "transaction_not_required": "False",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.all()[0].username, "How@12")
        self.assertEqual(Profile.objects.all()[0].profilename, "How@12")
        self.assertEqual(Profile.objects.all()[0].accessible, True)
        self.assertEqual(Profile.objects.all()[0].family_friendly, False)
        self.assertEqual(Profile.objects.all()[0].transaction_not_required, False)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(messages[0], "Your account has been updated!")

    def test_get_profile(self):
        """
        A user goes to the profile page and is able to see profile
        and rating information, including the rating title
        """
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        title = rr.title
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        Rating.objects.create(
            restroom_id=rr,
            user_id=user,
            rating="4",
            headline="headline1",
            comment="comment1",
        )
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, title)

    def test_profile_shows_claimed_restroom(self):
        """
        A user goes to the profile page and is able to see profile
        and claim information, including the titles of claimed restrooms
        """
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        title = rr.title
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        ClaimedRestroom.objects.create(restroom_id=rr, user_id=user, verified=True)
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, title)

    # def test_edit_rating_form(self):
    #     """
    #     A user can edit rating
    #     """
    #     desc = "TEST DESCRIPTION"
    #     yelp_id = "E6h-sMLmF86cuituw5zYxw"
    #     rr = create_restroom(yelp_id, desc)
    #     user = User.objects.create_user("Jon", "jon@email.com")
    #     self.client.force_login(user=user)
    #     Rating.objects.create(
    #         restroom_id=rr,
    #         user_id=user,
    #         rating="4",
    #         headline="headline1",
    #         comment="comment1",
    #     )
    #     response = self.client.get(reverse("accounts:edit_rating", args=(1,)))
    #     self.assertEqual(response.status_code, 200)

    # def test_edit_rating_edit(self):
    #     """
    #     A user can edit rating
    #     """
    #     desc = "TEST DESCRIPTION"
    #     yelp_id = "E6h-sMLmF86cuituw5zYxw"
    #     rr = create_restroom(yelp_id, desc)
    #     user = User.objects.create_user("Jon", "jon@email.com")
    #     self.client.force_login(user=user)
    #     Rating.objects.create(
    #         restroom_id=rr,
    #         user_id=user,
    #         rating="4",
    #         headline="headline1",
    #         comment="comment1",
    #     )
    #     response = self.client.post(
    #         reverse("accounts:edit_rating", args=(1,)),
    #         data={"rating": 5, "headline": "123", "comment": "456", },
    #     )
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(Rating.objects.all()[0].rating, 5)
    #     self.assertEqual(Rating.objects.all()[0].headline, "123")
    #     self.assertEqual(Rating.objects.all()[0].comment, "456")
    #     messages = [m.message for m in get_messages(response.wsgi_request)]
    #     self.assertIn(messages[0], "Your rating has been updated!")

    # def test_edit_non_existant_rating(self):
    #     """
    #     user A will receive 404 message when trying to edit rating does not exist
    #     """
    #     yelp_id = "E6h-sMLmF86cuituw5zYxw"
    #     desc = "Testing newly created restroom"
    #     new_restroom = create_restroom(yelp_id, desc)
    #     user1 = User.objects.create_user("Simon1", "simon1@email.com")
    #     self.client.force_login(user=user1)
    #     Rating.objects.create(
    #         restroom_id=new_restroom,
    #         user_id=user1,
    #         rating="1",
    #         headline="headline1",
    #         comment="comment1",
    #     )
    #     response = self.client.get(reverse("accounts:edit_rating", args=(10,)))
    #     self.assertEqual(response.status_code, 404)

    # def test_edit_rating_wrong_user(self):
    #     """
    #     user A will receive 404 message when trying to edit rating from user B
    #     """
    #     yelp_id = "E6h-sMLmF86cuituw5zYxw"
    #     desc = "Testing newly created restroom"
    #     new_restroom = create_restroom(yelp_id, desc)
    #     user1 = User.objects.create_user("Simon1", "simon1@email.com")
    #     user2 = User.objects.create_user("Simon2", "simon2@email.com")
    #     self.client.force_login(user=user2)
    #     Rating.objects.create(
    #         restroom_id=new_restroom,
    #         user_id=user1,
    #         rating="1",
    #         headline="headline1",
    #         comment="comment1",
    #     )
    #     response = self.client.get(reverse("accounts:edit_rating", args=(1,)))
    #     self.assertEqual(response.status_code, 404)

    # def test_delete_rating_wrong_user(self):
    #     """
    #     user A will receive 404 message when trying to delete rating from user B
    #     """
    #     yelp_id = "E6h-sMLmF86cuituw5zYxw"
    #     desc = "Testing newly created restroom"
    #     new_restroom = create_restroom(yelp_id, desc)
    #     user1 = User.objects.create_user("Simon1", "simon1@email.com")
    #     user2 = User.objects.create_user("Simon2", "simon2@email.com")
    #     self.client.force_login(user=user2)
    #     Rating.objects.create(
    #         restroom_id=new_restroom,
    #         user_id=user1,
    #         rating="1",
    #         headline="headline1",
    #         comment="comment1",
    #     )
    #     response = self.client.get(reverse("accounts:delete_rating", args=(1,)))
    #     self.assertEqual(response.status_code, 404)
