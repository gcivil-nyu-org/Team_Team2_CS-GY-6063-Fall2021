from naturescall.models import Restroom, Rating, ClaimedRestroom
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404

# from .forms import LocationForm
from .forms import AddRestroom, AddRating, ClaimRestroom
import requests
from django.contrib.auth.decorators import login_required
from .filters import RestroomFilter
from django.contrib import messages
from urllib.parse import urlencode

# import argparse
# import json
# import sys
# import urllib
# from urllib.error import HTTPError
from urllib.parse import quote

# from urllib.parse import urlencode
import os
from django.urls import reverse

api_key = str(os.getenv("yelp_key"))
map_embedded_key = str(os.getenv("map_embedded"))

API_HOST = "https://api.yelp.com"
SEARCH_PATH = "/v3/businesses/search"
BUSINESS_PATH = "/v3/businesses/"


# The index page
def index(request):
    context = {}
    # form = LocationForm(request.POST or None)
    # context["form"] = form
    return render(request, "naturescall/index.html", context)


# The search page for the user to enter address, search for and
# display the restrooms around the location
def search_restroom(request):
    context = {}
    if request.GET.get("searched") is not None:
        if not request.user.is_authenticated:
            map = str(os.getenv("map"))
            location = request.GET["searched"]
            tableFilter = RestroomFilter()
            k = search(api_key, '"restroom","food","public"', location, 20)
            data = []
            loc = []
            loc1 = []
            url = ""
            if not k.get("error"):
                data = k["businesses"]
                data.sort(key=getDistance)
                for restroom in data:
                    restroom["distance"] = int(restroom["distance"])
                    r_id = restroom["id"]
                    r_coordinates_lat = restroom["coordinates"]["latitude"]
                    r_coordinates_long = restroom["coordinates"]["longitude"]
                    loc.append(str(r_coordinates_lat) + "," + str(r_coordinates_long))
                    querySet = Restroom.objects.filter(yelp_id=r_id)
                    if not querySet:
                        restroom["our_rating"] = "no rating"
                        restroom["db_id"] = ""
                    else:
                        restroom["db_id"] = querySet.values()[0]["id"]
                    addr = str(restroom["location"]["display_address"])
                    restroom["addr"] = addr.translate(str.maketrans("", "", "[]'"))
                url = str(
                    google_url(
                        loc, loc1, width=800, height=740, center=location, key=map
                    )
                )
            context["location"] = location
            context["data"] = data
            context["tableFilter"] = tableFilter
            context["map"] = url
            request.session["search_location"] = location
            return render(request, "naturescall/search_restroom.html", context)
        else:
            dbRestroom = Restroom.objects.all()
            location = request.GET["searched"]
            profile = request.user.profile
            d = {
                "accessible": profile.accessible,
                "family_friendly": profile.family_friendly,
                "transaction_not_required": profile.transaction_not_required,
            }
            tableFilter = RestroomFilter(d, queryset=dbRestroom)
            map = str(os.getenv("map"))
            yelp_data = search(api_key, '"restroom","food","public"', location, 20)
            data = []
            data1 = []
            data2 = []
            loc = []
            loc1 = []
            url = ""
            if not yelp_data.get("error"):
                data1 = yelp_data["businesses"]
                data1.sort(key=getDistance)
                for restroom in data1:
                    restroom["distance"] = int(restroom["distance"])
                    r_id = restroom["id"]
                    querySet = Restroom.objects.filter(yelp_id=r_id)
                    if not querySet:
                        restroom["our_rating"] = "no rating"
                        restroom["db_id"] = ""
                    else:
                        restroom["db_id"] = querySet.values()[0]["id"]
                    addr = str(restroom["location"]["display_address"])
                    restroom["addr"] = addr.translate(str.maketrans("", "", "[]'"))
                id_obj_pairs = {}
                for obj in tableFilter.qs:
                    id = obj.id
                    id_obj_pairs[id] = obj
                for restroom in data1:
                    if restroom["db_id"] in id_obj_pairs:
                        data.append(restroom)
                        r_coordinates_lat = restroom["coordinates"]["latitude"]
                        r_coordinates_long = restroom["coordinates"]["longitude"]
                        loc1.append(
                            str(r_coordinates_lat) + "," + str(r_coordinates_long)
                        )
                    else:
                        data2.append(restroom)
                        r_coordinates_lat = restroom["coordinates"]["latitude"]
                        r_coordinates_long = restroom["coordinates"]["longitude"]
                        loc.append(
                            str(r_coordinates_lat) + "," + str(r_coordinates_long)
                        )
                url = str(
                    google_url(
                        loc, loc1, width=600, height=740, center=location, key=map
                    )
                )
            context["tableFilter"] = tableFilter
            context["data"] = data
            context["data1"] = data2
            context["map"] = url
            request.session["search_location"] = location
            return render(request, "naturescall/filtered_search.html", context)
    else:
        dbRestroom = Restroom.objects.all()
        tableFilter = RestroomFilter(request.GET, queryset=dbRestroom)
        location = request.session["search_location"]
        map = str(os.getenv("map"))
        yelp_data = search(api_key, '"restroom","food","public"', location, 20)
        data = []
        data1 = []
        data2 = []
        loc = []
        loc1 = []
        url = ""
        if not yelp_data.get("error"):
            data1 = yelp_data["businesses"]
            data1.sort(key=getDistance)
            for restroom in data1:
                restroom["distance"] = int(restroom["distance"])
                r_id = restroom["id"]
                querySet = Restroom.objects.filter(yelp_id=r_id)
                if not querySet:
                    restroom["our_rating"] = "no rating"
                    restroom["db_id"] = ""
                else:
                    restroom["db_id"] = querySet.values()[0]["id"]
                addr = str(restroom["location"]["display_address"])
                restroom["addr"] = addr.translate(str.maketrans("", "", "[]'"))
            id_obj_pairs = {}
            for obj in tableFilter.qs:
                id = obj.id
                id_obj_pairs[id] = obj
            for restroom in data1:
                if restroom["db_id"] in id_obj_pairs:
                    data.append(restroom)
                    r_coordinates_lat = restroom["coordinates"]["latitude"]
                    r_coordinates_long = restroom["coordinates"]["longitude"]
                    loc1.append(str(r_coordinates_lat) + "," + str(r_coordinates_long))
                else:
                    data2.append(restroom)
                    r_coordinates_lat = restroom["coordinates"]["latitude"]
                    r_coordinates_long = restroom["coordinates"]["longitude"]
                    loc.append(str(r_coordinates_lat) + "," + str(r_coordinates_long))
            url = str(
                google_url(loc, loc1, width=600, height=740, center=location, key=map)
            )
        context["tableFilter"] = tableFilter
        context["data"] = data
        context["data1"] = data2
        context["map"] = url
        return render(request, "naturescall/filtered_search.html", context)


"""def search_restroom(request):
    context = {}
    # form = LocationForm(request.POST or None)
    # location = request.POST["location"]
    if request.GET.get("searched") is not None:
        map = str(os.getenv("map"))
        location = request.GET["searched"]
        tableFilter = RestroomFilter()
        k = search(api_key, '"restroom","food","public"', location, 20)
        data = []
        loc = []
        loc1 = []
        if not k.get("error"):
            data = k["businesses"]
            # Sort by distance
            data.sort(key=getDistance)
        # Load rating data from our database
        for restroom in data:
            restroom["distance"] = int(restroom["distance"])
            # print(restroom["distance"])
            r_id = restroom["id"]
            r_coordinates_lat = restroom["coordinates"]["latitude"]
            r_coordinates_long = restroom["coordinates"]["longitude"]
            loc.append(str(r_coordinates_lat) + "," + str(r_coordinates_long))
            querySet = Restroom.objects.filter(yelp_id=r_id)
            if not querySet:
                restroom["our_rating"] = "no rating"
                restroom["db_id"] = ""
            else:
                # restroom["our_rating"] = querySet.values()[0]["rating"]
                restroom["db_id"] = querySet.values()[0]["id"]
                # print(restroom["db_id"])
            addr = str(restroom["location"]["display_address"])
            restroom["addr"] = addr.translate(str.maketrans("", "", "[]'"))
        # context["form"] = form
        url = str(
            google_url(loc, loc1, width=800, height=740, center=location, key=map)
        )
        context["location"] = location
        context["data"] = data
        context["tableFilter"] = tableFilter
        context["map"] = url
        request.session["search_location"] = location
        return render(request, "naturescall/search_restroom.html", context)
    else:
        dbRestroom = Restroom.objects.all()
        tableFilter = RestroomFilter(request.GET, queryset=dbRestroom)
        location = request.GET["filtered"]
        map = str(os.getenv("map"))
        yelp_data = search(api_key, '"restroom","food","public"', location, 20)
        data = []
        data1 = []
        data2 = []
        loc = []
        loc1 = []
        if not yelp_data.get("error"):
            data1 = yelp_data["businesses"]
            data1.sort(key=getDistance)
        for restroom in data1:
            restroom["distance"] = int(restroom["distance"])
            r_id = restroom["id"]
            querySet = Restroom.objects.filter(yelp_id=r_id)
            if not querySet:
                restroom["our_rating"] = "no rating"
                restroom["db_id"] = ""
            else:
                restroom["db_id"] = querySet.values()[0]["id"]
                restroom["accessible"] = querySet.values()[0]["accessible"]
                restroom["family_friendly"] = querySet.values()[0]["family_friendly"]
                restroom["transaction_not_required"] = querySet.values()[0][
                    "transaction_not_required"
                ]
            addr = str(restroom["location"]["display_address"])
            restroom["addr"] = addr.translate(str.maketrans("", "", "[]'"))
        id_obj_pairs = {}
        for obj in tableFilter.qs:
            id = obj.id
            id_obj_pairs[id] = obj
        for restroom in data1:
            if restroom["db_id"] in id_obj_pairs:
                data.append(restroom)
                r_coordinates_lat = restroom["coordinates"]["latitude"]
                r_coordinates_long = restroom["coordinates"]["longitude"]
                loc1.append(str(r_coordinates_lat) + "," + str(r_coordinates_long))
            else:
                data2.append(restroom)
                r_coordinates_lat = restroom["coordinates"]["latitude"]
                r_coordinates_long = restroom["coordinates"]["longitude"]
                loc.append(str(r_coordinates_lat) + "," + str(r_coordinates_long))
        url = str(
            google_url(loc, loc1, width=600, height=740, center=location, key=map)
        )
        context["tableFilter"] = tableFilter
        context["data"] = data
        context["data1"] = data2
        context["map"] = url
        request.session["search_location"] = location
        return render(request, "naturescall/filtered_search.html", context)
"""

# Filtered search results-:
"""def filter_restroom(request):
    dbRestroom = Restroom.objects.all()
    tableFilter = RestroomFilter(request.GET, queryset=dbRestroom)
    location = request.GET.get("filtered")
    map = str(os.getenv("map"))
    yelp_data = search(api_key, '"restroom","food","public"', location, 20)
    data = []
    data1 = []
    data2 = []
    loc = []
    loc1 = []
    if not yelp_data.get("error"):
        data1 = yelp_data["businesses"]
        data1.sort(key=getDistance)
    for restroom in data1:
        restroom["distance"] = int(restroom["distance"])
        r_id = restroom["id"]
        querySet = Restroom.objects.filter(yelp_id=r_id)
        if not querySet:
            restroom["our_rating"] = "no rating"
            restroom["db_id"] = ""
        else:
            restroom["db_id"] = querySet.values()[0]["id"]
            restroom["accessible"] = querySet.values()[0]["accessible"]
            restroom["family_friendly"] = querySet.values()[0]["family_friendly"]
            restroom["transaction_not_required"] = querySet.values()[0][
                "transaction_not_required"
            ]
        addr = str(restroom["location"]["display_address"])
        restroom["addr"] = addr.translate(str.maketrans("", "", "[]'"))
    id_obj_pairs = {}
    for obj in tableFilter.qs:
        id = obj.id
        id_obj_pairs[id] = obj
    for restroom in data1:
        if restroom["db_id"] in id_obj_pairs:
            data.append(restroom)
            r_coordinates_lat = restroom["coordinates"]["latitude"]
            r_coordinates_long = restroom["coordinates"]["longitude"]
            loc1.append(str(r_coordinates_lat) + "," + str(r_coordinates_long))
        else:
            data2.append(restroom)
            r_coordinates_lat = restroom["coordinates"]["latitude"]
            r_coordinates_long = restroom["coordinates"]["longitude"]
            loc.append(str(r_coordinates_lat) + "," + str(r_coordinates_long))
    url = str(google_url(loc, loc1, width=600, height=740, center=location, key=map))
    context = {"tableFilter": tableFilter, "data": data, "data1": data2, "map": url}
    request.session["search_location"] = location
    return render(request, "naturescall/filtered_search.html", context)
"""


@login_required(login_url="login")
def rate_restroom(request, r_id):
    """Rate a restroom"""
    current_restroom = get_object_or_404(Restroom, id=r_id)
    current_user = request.user
    rating_set = Rating.objects.filter(restroom_id=r_id, user_id=current_user)
    if request.method == "POST":
        form = AddRating(data=request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user_id = current_user
            entry.restroom_id = current_restroom
            if rating_set:
                entry.id = rating_set[0].id
            entry.save()
            msg = "Congratulations, Your rating has been saved!"
            messages.success(request, f"{msg}")
            if request.session["referer"] and "profile" in request.session["referer"]:
                return redirect("accounts:profile")
            else:
                return redirect("naturescall:restroom_detail", r_id=current_restroom.id)
    else:
        request.session["referer"] = request.headers.get("Referer")
        if rating_set:
            form = AddRating(instance=rating_set[0])
        else:
            form = AddRating()
    context = {"form": form, "title": current_restroom.title}
    return render(request, "naturescall/rate_restroom.html", context)


@login_required
def delete_rating(request, r_id):
    """delete a restroom rating"""
    current_user = request.user
    rating_set = Rating.objects.filter(restroom_id=r_id, user_id=current_user)
    if not rating_set:
        raise Http404("Sorry, no rating exists")
    rating_entry = rating_set[0]
    rating_entry.delete()
    msg = "Your rating has been deleted!"
    messages.success(request, f"{msg}")
    return HttpResponseRedirect(reverse("naturescall:index"))


# The page for adding / updating restroom
@login_required(login_url="login")
def add_restroom(request, yelp_id):
    # check to see if restaurant already exists in database
    current_restroom_set = Restroom.objects.filter(yelp_id=yelp_id)
    # make sure if this is a modification that the restroom
    # is claimed and the user is the owner
    if current_restroom_set:
        current_user = request.user
        valid_claim = ClaimedRestroom.objects.filter(
            restroom_id=current_restroom_set[0], user_id=current_user, verified=True
        )
        if not valid_claim:
            raise Http404("Access Denied")
    if request.method == "POST":
        form = AddRestroom(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            if current_restroom_set:
                entry.id = current_restroom_set[0].id
                entry.save()
                return redirect(
                    "naturescall:manage_restroom", r_id=current_restroom_set[0].id
                )
            entry.save()
            return HttpResponseRedirect(reverse("naturescall:index"))
        else:
            return render(request, "naturescall/add_restroom.html", {"form": form})
    else:
        if not current_restroom_set:
            k = get_business(api_key, yelp_id)
            if k.get("error"):
                raise Http404("Restroom does not exist")
            title = (
                k["name"]
                + " "
                + k["location"]["address1"]
                + " "
                + k["location"]["city"]
            )
            form = AddRestroom(initial={"yelp_id": yelp_id, "title": title})
        else:
            form = AddRestroom(instance=current_restroom_set[0])
            title = current_restroom_set[0].title
        context = {"form": form, "title": title}
        return render(request, "naturescall/add_restroom.html", context)


def calculate_rating(r_id):
    querySet = Rating.objects.filter(restroom_id=r_id)
    if querySet:
        average_rating = 0
        for rating in querySet.values():
            average_rating += rating["rating"]
        average_rating = average_rating / len(querySet)
        return round(average_rating, 1)
    else:
        return "N/A"


# The page for showing one restroom details
def restroom_detail(request, r_id):
    """Show a single restroom"""
    current_restroom = get_object_or_404(Restroom, id=r_id)
    current_user = request.user
    res = {}
    yelp_id = current_restroom.yelp_id
    yelp_data = get_business(api_key, yelp_id)
    yelp_data["db_id"] = r_id
    yelp_data["rating"] = calculate_rating(r_id)
    yelp_data["accessible"] = current_restroom.accessible
    yelp_data["family_friendly"] = current_restroom.family_friendly
    yelp_data["transaction_not_required"] = current_restroom.transaction_not_required

    res["yelp_data"] = yelp_data
    addr = str(yelp_data["location"]["display_address"])
    res["addr"] = addr.translate(str.maketrans("", "", "[]'"))
    res["desc"] = current_restroom.description

    # determine if claim button should be shown
    # should not be shown to an unauthenticated user
    show_claim = current_user.is_authenticated
    # should not be shown if any user has a verified claim
    # should not be shown if this user has a previous unverified claim
    all_claims = ClaimedRestroom.objects.filter(restroom_id=current_restroom)
    for claim in all_claims:
        if claim.verified or claim.user_id == current_user:
            show_claim = False

    ratings = Rating.objects.filter(restroom_id=r_id)
    context = {
        "res": res,
        "ratings": ratings,
        "map_key": map_embedded_key,
        "show_claim": show_claim,
    }
    return render(request, "naturescall/restroom_detail.html", context)


@login_required
def claim_restroom(request, r_id):
    """claim a restroom"""
    current_restroom = get_object_or_404(Restroom, id=r_id)
    current_claims = ClaimedRestroom.objects.filter(
        restroom_id=current_restroom, verified=True
    )
    if current_claims:
        raise Http404("Access Denied")
    current_user = request.user
    if request.method == "POST":
        form = ClaimRestroom(request.POST)
        if form.is_valid():
            claim = ClaimedRestroom()
            claim.restroom_id = current_restroom
            claim.user_id = current_user
            claim.save()
            return redirect("naturescall:restroom_detail", r_id=r_id)
    else:
        form = ClaimRestroom()
    context = {"form": form, "title": current_restroom.title}
    return render(request, "naturescall/claim_restroom.html", context)


@login_required
def manage_restroom(request, r_id):
    """manage a restroom"""
    current_restroom = get_object_or_404(Restroom, id=r_id)
    current_user = request.user
    valid_claim = ClaimedRestroom.objects.filter(
        restroom_id=current_restroom, user_id=current_user, verified=True
    )
    if not valid_claim:
        raise Http404("Access Denied")
    context = {
        "title": current_restroom.title,
        "yelp_id": current_restroom.yelp_id,
        "r_id": current_restroom.id,
    }
    return render(request, "naturescall/manage_restroom.html", context)


@login_required
def comment_response(request, r_id):
    """manage a restroom"""
    current_restroom = get_object_or_404(Restroom, id=r_id)
    current_user = request.user
    valid_claim = ClaimedRestroom.objects.filter(
        restroom_id=current_restroom, user_id=current_user, verified=True
    )
    if not valid_claim:
        raise Http404("Access Denied")
    all_ratings = Rating.objects.filter(restroom_id=current_restroom)
    all_comments = [rating.comment for rating in all_ratings]
    context = {
        "title": current_restroom.title,
        "r_id": r_id,
        "comments": all_comments,
        "ratings": all_ratings,
    }
    return render(request, "naturescall/comment_response.html", context)


# Helper function: make an API request
def request(host, path, api_key, url_params=None):
    url_params = url_params or {}
    url = "{0}{1}".format(host, quote(path.encode("utf8")))
    headers = {
        "Authorization": "Bearer %s" % api_key,
    }
    response = requests.request("GET", url, headers=headers, params=url_params)
    return response.json()


# Helper function: fetch searched data with given parameters - search keywords
# as term, address as loaction, and number of data entries to fetch as num
def style_marker(locat, style_options={}):
    opts = ["%s:%s" % (k, v) for k, v in style_options.items()]
    opts.append(locat)
    return "|".join(opts)


def google_url(loc, loc1, width, height, center, key, maptype="roadmap"):
    gmap_url = "https://maps.googleapis.com/maps/api/staticmap"
    size_str = str(width) + "x" + str(height)
    markers_objects = []
    obj = style_marker(center, style_options={"color": "red", "label": "S"})
    markers_objects.append(obj)
    for loc2 in loc:
        obj = style_marker(loc2, style_options={"color": "green", "label": "R"})
        markers_objects.append(obj)
    if loc1:
        for l1 in loc1:
            obj = style_marker(l1, style_options={"color": "orange", "label": "F"})
            markers_objects.append(obj)
    mapopts = {
        "center": center,
        "size": size_str,
        "markers": markers_objects,
        "maptype": maptype,
        "key": key,
    }
    query_str = urlencode(mapopts, doseq=True)
    return gmap_url + "?" + query_str


def search(api_key, term, location, num):
    url_params = {
        "term": term.replace(" ", "+"),
        "location": location.replace(" ", "+"),
        "limit": num,
        "radius": 500,
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


# Helper function: fetch one single business using the business id
def get_business(api_key, business_id):
    business_path = BUSINESS_PATH + business_id
    return request(API_HOST, business_path, api_key)


# Helper function: get restroom distance from the searched location
def getDistance(restroom_dic):
    return restroom_dic["distance"]
