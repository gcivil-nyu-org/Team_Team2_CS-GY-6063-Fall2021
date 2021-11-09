from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from .models import Profile
from naturescall.models import Rating, Restroom

# Create your tests here.


def create_restroom(yelp_id, desc):
    """
    Create a restroom with the given parameters. Other parameters are
    left at their default values
    """
    return Restroom.objects.create(yelp_id=yelp_id, description=desc)


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

    def test_delete_rating(self):
        """
        A user can delete rating
        """
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        Rating.objects.create(
            restroom_id=rr,
            user_id=user,
            rating="4",
            headline="headline1",
            comment="comment1",
        )
        response = self.client.get(reverse("accounts:delete_rating", args=(1,)))
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(messages[0], "Your rating has been deleted!")

    def test_edit_rating_form(self):
        """
        A user can edit rating
        """
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        Rating.objects.create(
            restroom_id=rr,
            user_id=user,
            rating="4",
            headline="headline1",
            comment="comment1",
        )
        response = self.client.get(reverse("accounts:edit_rating", args=(1,)))
        self.assertEqual(response.status_code, 200)

    def test_edit_rating_edit(self):
        """
        A user can edit rating
        """
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        Rating.objects.create(
            restroom_id=rr,
            user_id=user,
            rating="4",
            headline="headline1",
            comment="comment1",
        )
        response = self.client.post(
            reverse("accounts:edit_rating", args=(1,)),
            data={"rating": 5, "headline": "123", "comment": "456", },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Rating.objects.all()[0].rating, 5)
        self.assertEqual(Rating.objects.all()[0].headline, "123")
        self.assertEqual(Rating.objects.all()[0].comment, "456")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(messages[0], "Your rating has been updated!")

    def edit_non_existant_rating(self):
        """
        user A will receive 404 message when trying to edit rating does not exist
        """
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        desc = "Testing newly created restroom"
        new_restroom = create_restroom(yelp_id, desc)
        user1 = User.objects.create_user("Simon1", "simon1@email.com")
        self.client.force_login(user=user1)
        Rating.objects.create(
            restroom_id=new_restroom,
            user_id=user1,
            rating="1",
            headline="headline1",
            comment="comment1",
        )
        response = self.client.get(reverse("accounts:edit_rating", args=(10,)))
        self.assertEqual(response.status_code, 404)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(messages[0], "Sorry, the rating does not exist")

    def delete_non_existant_rating(self):
        """
        user A will receive 404 message when trying to delete rating does not exist
        """
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        desc = "Testing newly created restroom"
        new_restroom = create_restroom(yelp_id, desc)
        user1 = User.objects.create_user("Simon1", "simon1@email.com")
        self.client.force_login(user=user1)
        Rating.objects.create(
            restroom_id=new_restroom,
            user_id=user1,
            rating="1",
            headline="headline1",
            comment="comment1",
        )
        response = self.client.get(reverse("accounts:delete_rating", args=(10,)))
        self.assertEqual(response.status_code, 404)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(messages[0], "Sorry, the rating does not exist")

    def edit_rating_wrong_user(self):
        """
        user A will receive 404 message when trying to edit rating from user B
        """
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        desc = "Testing newly created restroom"
        new_restroom = create_restroom(yelp_id, desc)
        user1 = User.objects.create_user("Simon1", "simon1@email.com")
        user2 = User.objects.create_user("Simon2", "simon2@email.com")
        self.client.force_login(user=user2)
        Rating.objects.create(
            restroom_id=new_restroom,
            user_id=user1,
            rating="1",
            headline="headline1",
            comment="comment1",
        )
        response = self.client.get(reverse("accounts:edit_rating", args=(1,)))
        self.assertEqual(response.status_code, 404)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(
            messages[0], "Sorry, you do not have the right to edit this rating"
        )

    def delete_rating_wrong_user(self):
        """
        user A will receive 404 message when trying to delete rating from user B
        """
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        desc = "Testing newly created restroom"
        new_restroom = create_restroom(yelp_id, desc)
        user1 = User.objects.create_user("Simon1", "simon1@email.com")
        user2 = User.objects.create_user("Simon2", "simon2@email.com")
        self.client.force_login(user=user2)
        Rating.objects.create(
            restroom_id=new_restroom,
            user_id=user1,
            rating="1",
            headline="headline1",
            comment="comment1",
        )
        response = self.client.get(reverse("accounts:delete_rating", args=(1,)))
        self.assertEqual(response.status_code, 404)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(
            messages[0], "Sorry, you do not have the right to delete this rating"
        )
