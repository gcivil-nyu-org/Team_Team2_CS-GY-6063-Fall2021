from naturescall.models import Restroom, Rating
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404

# from .forms import LocationForm
from .forms import AddRestroom, AddRating
import requests
from django.contrib.auth.decorators import login_required
from .filters import RestroomFilter
from django.contrib import messages

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
    # form = LocationForm(request.POST or None)
    # location = request.POST["location"]
    if request.POST.get("searched") is not None:
        location = request.POST["searched"]
        tableFilter = RestroomFilter()
        k = search(api_key, '"restroom","food","public"', location, 20)
        data = []
        if not k.get("error"):
            data = k["businesses"]
            # Sort by distance
            data.sort(key=getDistance)
        # Load rating data from our database
        for restroom in data:
            restroom["distance"] = int(restroom["distance"])
            # print(restroom["distance"])
            r_id = restroom["id"]
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
        context["location"] = location
        context["data"] = data
        context["tableFilter"] = tableFilter
        return render(request, "naturescall/search_restroom.html", context)
    else:
        dbRestroom = Restroom.objects.all()
        tableFilter = RestroomFilter(request.GET, queryset=dbRestroom)
        location = request.GET["filtered"]
        yelp_data = search(api_key, '"restroom","food","public"', location, 20)
        data = []
        data1 = []
        data2 = []
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
        for obj in tableFilter.qs:
            for restroom in data1:
                if restroom["db_id"] == obj.id:
                    data.append(restroom)
                else:
                    data2.append(restroom)
        context["tableFilter"] = tableFilter
        context["data"] = data
        context["data1"] = data2
        return render(request, "naturescall/filtered_search.html", context)


# Filtered search results-:
def filter_restroom(request):
    dbRestroom = Restroom.objects.all()
    tableFilter = RestroomFilter(request.GET, queryset=dbRestroom)
    location = request.GET["filtered"]
    yelp_data = search(api_key, '"restroom","food","public"', location, 20)
    data = []
    data1 = []
    data2 = []
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

    for obj in tableFilter.qs:
        for restroom in data1:
            if restroom["db_id"] == obj.id:
                data.append(restroom)
            else:
                data2.append(restroom)
    context = {"tableFilter": tableFilter, "data": data, "data1": data2}
    return render(request, "naturescall/filtered_search.html", context)


@login_required(login_url="login")
def rate_restroom(request, r_id):
    """Rate a restroom"""
    current_restroom = get_object_or_404(Restroom, id=r_id)
    current_user = request.user
    if request.method == "POST":
        form = AddRating(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.user_id = current_user
            new_entry.restroom_id = current_restroom
            new_entry.save()
            msg = "Congratulations, Your rating has been saved!"
            messages.success(request, f"{msg}")
            return redirect("naturescall:restroom_detail", r_id=current_restroom.id)
    else:
        # check for redundant rating
        querySet = Rating.objects.filter(restroom_id=r_id, user_id=current_user)
        if querySet:
            msg = "Sorry, You have already rated this restroom!!"
            messages.success(request, f"{msg}")
            return redirect("naturescall:restroom_detail", r_id=current_restroom.id)

    form = AddRating()
    context = {"form": form, "title": current_restroom.title}
    return render(request, "naturescall/rate_restroom.html", context)


# The page for adding new restroom to our database
@login_required(login_url="login")
def add_restroom(request, r_id):
    if request.method == "POST":
        f = AddRestroom(request.POST)
        if f.is_valid():
            post = f.save(commit=False)
            post.save()
            return HttpResponseRedirect(reverse("naturescall:index"))
        else:
            return render(request, "naturescall/add_restroom.html", {"form": f})
    else:
        k = get_business(api_key, r_id)
        if k.get("error"):
            raise Http404("Restroom does not exist")
        context = {}
        name = k["name"]
        title = (
            k["name"] + " " + k["location"]["address1"] + " " + k["location"]["city"]
        )
        form = AddRestroom(initial={"yelp_id": r_id, "title": title})
        context["form"] = form
        context["name"] = name
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
    querySet = Restroom.objects.filter(id=r_id)
    res = {}
    if querySet:
        yelp_id = querySet.values()[0]["yelp_id"]
        yelp_data = get_business(api_key, yelp_id)
        yelp_data["db_id"] = r_id
        yelp_data["rating"] = calculate_rating(r_id)
        yelp_data["accessible"] = querySet.values()[0]["accessible"]
        yelp_data["family_friendly"] = querySet.values()[0]["family_friendly"]
        yelp_data["transaction_not_required"] = querySet.values()[0][
            "transaction_not_required"
        ]

        res["yelp_data"] = yelp_data
        addr = str(yelp_data["location"]["display_address"])
        res["addr"] = addr.translate(str.maketrans("", "", "[]'"))
        res["desc"] = querySet.values()[0]["description"]
    else:
        raise Http404("Restroom does not exist")

    ratings = Rating.objects.filter(restroom_id=r_id)
    context = {"res": res, "ratings": ratings}
    return render(request, "naturescall/restroom_detail.html", context)


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
