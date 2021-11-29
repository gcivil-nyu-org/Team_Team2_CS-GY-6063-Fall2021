from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from .models import Restroom, Rating, ClaimedRestroom, Coupon
from .filters import RestroomFilter
import os

api_key = str(os.getenv("yelp_key"))

API_HOST = "https://api.yelp.com"
SEARCH_PATH = "/v3/businesses/search"
BUSINESS_PATH = "/v3/businesses/"


def create_restroom(yelp_id, desc):
    """
    Create a restroom with the given parameters. Other parameters are
    left at their default values
    """
    return Restroom.objects.create(yelp_id=yelp_id, description=desc)


class ViewTests(TestCase):
    def test_index(self):
        """
        If index is fetched, the response should contain welcome message"
        """
        response = self.client.get(reverse("naturescall:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to Nature's call")

    def test_missing_restroom(self):
        """
        If the selected restroom is not present in the database,
        the response should be a 404 Error
        """
        response = self.client.get(reverse("naturescall:restroom_detail", args=(1,)))
        self.assertEqual(response.status_code, 404)

    def test_one_restroom_via_create(self):
        """
        Once a restroom is added using create, it should be
        reachable via the restroom_detail link
        """
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        create_restroom(yelp_id, desc)
        response = self.client.get(reverse("naturescall:restroom_detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["res"]["desc"], desc)

    def test_one_restroom_via_form_not_logged_in(self):
        """
        Trying to add a restroom via the form when not logged in
        should result in a redirect to the login page. That restroom's
        page then should not exist.
        """
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        response = self.client.post(
            reverse("naturescall:add_restroom", args=(1,)),
            data={"yelp_id": yelp_id, "Description": desc},
        )
        response2 = self.client.get(reverse("naturescall:restroom_detail", args=(1,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response2.status_code, 404)

    def test_one_restroom_via_form_logged_in(self):
        """
        A logged in user should be able to add a restroom via the form.
        Once added, the restroom page should be accessible.
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        title = "TEST TITLE"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        response = self.client.post(
            reverse("naturescall:add_restroom", args=(1,)),
            data={"yelp_id": yelp_id, "description": desc, "title": title},
        )
        response2 = self.client.get(reverse("naturescall:restroom_detail", args=(1,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, desc)

    def test_one_restroom_via_form_logged_in_get(self):
        """
        A logged in user should be able to see the page to
        add a restroom via the form.
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        response = self.client.get(
            reverse("naturescall:add_restroom", args=(yelp_id,)),
        )
        self.assertEqual(response.status_code, 200)

    def test_one_restroom_invalid_form_logged_in(self):
        """
        A restroom with an invalid description should not be added
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "9LTRDESCR"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        response = self.client.post(
            reverse("naturescall:add_restroom", args=(1,)),
            data={"yelp_id": yelp_id, "description": desc},
        )
        response2 = self.client.get(reverse("naturescall:restroom_detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response2.status_code, 404)

    def test_restroom_invalid_search(self):
        """
        A search with an invalid search string should yield no results
        but should return a valid webpage
        """
        response = self.client.get(
            reverse("naturescall:search_restroom"), data={"searched": "szzzzz"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Location Not Found")

    def test_restroom_valid_search_empty_database(self):
        """
        A search with a valid search string with an empty database
        should return a valid webpage with 20 "Add Restroom" results
        """
        response = self.client.get(
            reverse("naturescall:search_restroom"),
            data={"searched": "washington square park"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.content).count("Add Restroom"), 20)

    def test_restroom_valid_search_one_element_database(self):
        """
        A search with a valid search string with a database with one element
        should return a valid webpage with 19 "Add Restroom" results
        """
        desc = "TEST DESCRIPTION"
        yelp_id = "FkA9aoMhWO4XKFMTuTnl4Q"
        create_restroom(yelp_id, desc)
        response = self.client.get(
            reverse("naturescall:search_restroom"),
            data={"searched": "washigton square park"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.content).count("Add Restroom"), 19)

    def test_get_request_add_restroom_not_logged_in(self):
        """
        A get request to the add_restroom page should yield a
        redirect if the user is not logged in
        """
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        response = self.client.get(reverse("naturescall:add_restroom", args=(yelp_id,)))
        self.assertEqual(response.status_code, 302)

    def test_get_request_add_restroom_logged_in(self):
        """
        A get request to the add_restroom page should yield a
        valid response if the user is logged in
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        response = self.client.get(reverse("naturescall:add_restroom", args=(yelp_id,)))
        self.assertEqual(response.status_code, 200)

    def test_get_request_add_restroom_logged_in_invalid_id(self):
        """
        A get request to the add_restroom page should yield a
        404 error if the user is logged in but supplies an invalid yelp ID
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        yelp_id = "E6h-sMLmF86cuituw5zYxwXXXXXX"
        response = self.client.get(reverse("naturescall:add_restroom", args=(yelp_id,)))
        self.assertEqual(response.status_code, 404)

    def test_get_rating_one_restroom(self):
        """
        Once a restroom is added using create, it should be
        visible via the rate_restroom link
        """
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        create_restroom(yelp_id, desc)
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        response = self.client.get(reverse("naturescall:rate_restroom", args=(1,)))
        self.assertEqual(response.status_code, 200)

    def test_post_rating_one_restroom(self):
        """
        Once a restroom is added using create, it should be
        rateable using the restroom_detail link
        """
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        create_restroom(yelp_id, desc)
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        response = self.client.post(
            reverse("naturescall:rate_restroom", args=(1,)),
            data={
                "rating": "4",
                "headline": "headline1",
                "comment": "comment1",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Rating.objects.all()), 1)
        self.assertEqual(Rating.objects.all()[0].headline, "headline1")

    def test_seeing_previously_rated_restroom(self):
        """
        Once a restroom has been rated, the same user should be able
        to see that rating
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
        response = self.client.get(reverse("naturescall:rate_restroom", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Rating.objects.all()[0].headline, "headline1")

    def test_rating_previously_rated_restroom(self):
        """
        Once a restroom has been rated, that rating should be
        editable using the restroom_detail link
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
            reverse("naturescall:rate_restroom", args=(1,)),
            data={
                "rating": "2",
                "headline": "headline2",
                "comment": "comment2",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Rating.objects.all()), 1)
        self.assertEqual(Rating.objects.all()[0].headline, "headline2")

    def test_delete_non_existent_rating(self):
        """
        user A will receive 404 message when trying to delete rating does not exist
        """
        user1 = User.objects.create_user("Simon1", "simon1@email.com")
        self.client.force_login(user=user1)
        response = self.client.get(reverse("naturescall:delete_rating", args=(1,)))
        self.assertEqual(response.status_code, 404)

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
        response = self.client.get(reverse("naturescall:delete_rating", args=(1,)))
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(messages[0], "Your rating has been deleted!")

    def test_restroom_rating_calculation(self):
        """
        A restroom's rating should be the average of all users' ratings
        """
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        user1 = User.objects.create_user("Jon1", "jon1@email.com")
        user2 = User.objects.create_user("Jon2", "jon2@email.com")
        self.client.force_login(user=user1)
        Rating.objects.create(
            restroom_id=rr,
            user_id=user1,
            rating="1",
            headline="headline1",
            comment="comment1",
        )
        self.client.force_login(user=user2)
        Rating.objects.create(
            restroom_id=rr,
            user_id=user2,
            rating="4",
            headline="headline2",
            comment="comment2",
        )
        response = self.client.get(reverse("naturescall:restroom_detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rating: 2.5")

    def test_restroom_filter(self):
        """to check RestroomFilter is retrieving correct restroom"""
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        desc = "TEST Accessibile= true"
        r1 = Restroom.objects.create(
            yelp_id=yelp_id, description=desc, accessible="True"
        )
        qs = Restroom.objects.all()
        data = {
            "accessible": "True",
            "family_friendly": "False",
            "transaction_not_required": "False",
        }
        f = RestroomFilter(data, queryset=qs)
        self.assertEqual(f.qs[0], r1)

    def test_unauthenticated_user_search_restroom(self):
        """testing search result for unauthenticated user"""
        response = self.client.get(
            reverse("naturescall:search_restroom"),
            data={"searched": "washigton square park"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["data"]), 20)

    def test_unauthenticated_filter_search_restroom(self):
        """Testing filter search for unauthenticated user"""
        yelp_id = "FkA9aoMhWO4XKFMTuTnl4Q"
        desc = "TEST Accessibile= true"
        session = self.client.session
        session["search_location"] = "washigton square park"
        session.save()
        Restroom.objects.create(yelp_id=yelp_id, description=desc, accessible="True")
        data = {
            "location": session["search_location"],
            "accessible": "True",
            "family_friendly": "False",
            "transaction_not_required": "False",
        }
        response = self.client.get(reverse("naturescall:search_restroom"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["data"]), 1)
        self.assertEqual(len(response.context["data1"]), 19)

    def test_authenticated_user_search_restroom(self):
        """testing search result for authenticated user"""
        yelp_id = "FkA9aoMhWO4XKFMTuTnl4Q"
        desc = "TEST Accessibile= true"
        user = User.objects.create_user("Howard", "howard@gmail.com")
        self.client.force_login(user=user)
        self.client.post(
            reverse("accounts:profile"),
            data={
                "email": "Hao@gmail.com",
                "profilename": "Howard",
                "accessible": "True",
                "family_friendly": "False",
                "transaction_not_required": "False",
            },
        )

        Restroom.objects.create(yelp_id=yelp_id, description=desc, accessible="True")
        data = {"searched": "washigton square park"}
        response = self.client.get(reverse("naturescall:search_restroom"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["data"]), 1)
        self.assertEqual(len(response.context["data1"]), 19)

    def test_newly_created_restroom_with_no_rating(self):
        """
        A newly created restroom should have no rating
        """
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        desc = "Testing newly created restroom"
        new_restroom = create_restroom(yelp_id, desc)
        self.assertEqual(len(Rating.objects.filter(restroom_id=new_restroom.pk)), 0)

    def test_multiple_ratings_shown_in_restroom_detail(self):
        """
        If there are multiple ratings created
        """
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        desc = "Testing newly created restroom"
        new_restroom = create_restroom(yelp_id, desc)
        user1 = User.objects.create_user("Simon1", "simon1@email.com")
        user2 = User.objects.create_user("Simon2", "simon2@email.com")
        self.client.force_login(user=user1)
        Rating.objects.create(
            restroom_id=new_restroom,
            user_id=user1,
            rating="1",
            headline="headline1",
            comment="comment1",
        )
        self.client.force_login(user=user2)
        Rating.objects.create(
            restroom_id=new_restroom,
            user_id=user2,
            rating="4",
            headline="headline2",
            comment="comment2",
        )
        self.assertEqual(len(Rating.objects.filter(restroom_id=new_restroom.pk)), 2)

    def test_see_claim_button_unclaimed_restroom(self):
        """
        A get request to the restroom_detail page should yield a
        valid response containing "Claim This Restroom!"
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        create_restroom(yelp_id, desc)
        response = self.client.get(reverse("naturescall:restroom_detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Claim This Restroom!")

    def test_see_claim_button_unverified_restroom_claimed_by_self(self):
        """
        A get request to the restroom_detail page should yield a
        valid response but not "Claim This Restroom!" since this user has
        already put in a claim
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        ClaimedRestroom.objects.create(restroom_id=rr, user_id=user)
        response = self.client.get(reverse("naturescall:restroom_detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Claim This Restroom!")

    def test_see_claim_button_unverified_restroom_claimed_by_other(self):
        """
        A get request to the restroom_detail page should yield a
        valid response and "Claim This Restroom!" since some user has
        already put in an unverified claim
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        ClaimedRestroom.objects.create(restroom_id=rr, user_id=user)
        user1 = User.objects.create_user("Jon1", "jon1@email.com")
        self.client.force_login(user=user1)
        response = self.client.get(reverse("naturescall:restroom_detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Claim This Restroom!")

    def test_see_claim_button_verified_restroom_claimed_by_other(self):
        """
        A get request to the restroom_detail page should yield a
        valid response but not "Claim This Restroom!" since some user has
        already put in a verified claim
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        ClaimedRestroom.objects.create(restroom_id=rr, user_id=user, verified=True)
        user1 = User.objects.create_user("Jon1", "jon1@email.com")
        self.client.force_login(user=user1)
        response = self.client.get(reverse("naturescall:restroom_detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Claim This Restroom!")

    def test_enter_claim_get(self):
        """
        A get request to the claim_restroom page should yield a
        valid response
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        create_restroom(yelp_id, desc)
        response = self.client.get(reverse("naturescall:claim_restroom", args=(1,)))
        self.assertEqual(response.status_code, 200)

    def test_enter_claim_post(self):
        """
        A post request to the claim_restroom page should yield a
        redirect response
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        response = self.client.post(
            reverse("naturescall:claim_restroom", args=(1,)),
            data={
                "restroom_id": rr,
                "user_id": user,
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_enter_claim_get_restroom_already_claimed(self):
        """
        A get request to the claim_restroom page should yield a
        404 response if the restroom has already been claimed
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        ClaimedRestroom.objects.create(restroom_id=rr, user_id=user, verified=True)
        response = self.client.get(reverse("naturescall:claim_restroom", args=(1,)))
        self.assertEqual(response.status_code, 404)

    def test_view_add_restroom_page_unauthorized(self):
        """
        A non-owner should NOT be able to access the
        add_restroom page for a previously added restroom
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        create_restroom(yelp_id, desc)
        response = self.client.get(
            reverse("naturescall:add_restroom", args=(yelp_id,)),
        )
        self.assertEqual(response.status_code, 404)

    def test_view_add_restroom_page_authorized(self):
        """
        An owner should be able to access the
        add_restroom page for their previously added restroom
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        ClaimedRestroom.objects.create(restroom_id=rr, user_id=user, verified=True)
        response = self.client.get(
            reverse("naturescall:add_restroom", args=(yelp_id,)),
        )
        self.assertEqual(response.status_code, 200)

    def test_update_restroom_description_authorized(self):
        """
        The restroom owner should be able to update
        the description
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        title = "Restroom"
        rr = create_restroom(yelp_id, desc)
        ClaimedRestroom.objects.create(restroom_id=rr, user_id=user, verified=True)
        new_desc = "UPDATED DESCRIPTION"
        response = self.client.post(
            reverse("naturescall:add_restroom", args=(yelp_id,)),
            data={"yelp_id": yelp_id, "description": new_desc, "title": title},
        )
        updated_rr = Restroom.objects.get(id=1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(updated_rr.description, new_desc)

    def test_manage_restroom_authorized(self):
        """
        The restroom owner should be able to manage it
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        ClaimedRestroom.objects.create(restroom_id=rr, user_id=user, verified=True)
        response = self.client.get(
            reverse("naturescall:manage_restroom", args=(1,)),
        )
        self.assertEqual(response.status_code, 200)

    def test_manage_restroom_unauthorized(self):
        """
        A non-owner should not be able to manage a restroom
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        ClaimedRestroom.objects.create(restroom_id=rr, user_id=user, verified=True)
        user1 = User.objects.create_user("Jon1", "jon1@email.com")
        self.client.force_login(user=user1)
        response = self.client.get(
            reverse("naturescall:manage_restroom", args=(1,)),
        )
        self.assertEqual(response.status_code, 404)

    def test_get_qr(self):
        """
        A user is able to get qr code for a claimed restaurant with coupon
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        cr = ClaimedRestroom.objects.create(restroom_id=rr, user_id=user, verified=True)
        coupon = Coupon.objects.create(cr_id = cr, description = desc)
        response = self.client.get(
            reverse("naturescall:get_qr", args=(coupon.id,)),
        )
        self.assertEqual(response.status_code, 200)

    def test_confirm_qr(self):
        """
        A user is able to get scan the qr code for the coupon information
        """
        user = User.objects.create_user("Jon", "jon@email.com")
        self.client.force_login(user=user)
        desc = "TEST DESCRIPTION"
        yelp_id = "E6h-sMLmF86cuituw5zYxw"
        rr = create_restroom(yelp_id, desc)
        cr = ClaimedRestroom.objects.create(restroom_id=rr, user_id=user, verified=True)
        coupon = Coupon.objects.create(cr_id = cr, description = desc)
        response = self.client.get(
            reverse("naturescall:qr_confirm", args=(coupon.id,1)),
        )
        self.assertEqual(response.status_code, 200)
