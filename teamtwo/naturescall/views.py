from naturescall.models import Restroom
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import LocationForm
from .forms import AddRestroom
import requests
import argparse
import json
import sys
import urllib
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode
import os
from django.urls import reverse
api_key = str(os.getenv('yelp_key'))

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'


# The index page
def index(request):
    context = {}
    form = LocationForm(request.POST or None)
    context['form'] = form
    return render(request, "naturescall/index.html", context)


# The page for search and displaying restroom search results
def search_restroom(request):
    context = {}
    form = LocationForm(request.POST or None)
    location = request.POST['location']

    k = search(api_key, '"restroom","food","public"', location, 20)

    data = []

    if not k.get('error'):
        data = k['businesses']
        # Sort by distance
        data.sort(key = getDistance)

    print("The returned json obj is: \n {}".format(data))
    print("End of returned json obj \n")


    # Load rating data from our database
    for restroom in data:
        restroom['distance'] = int(restroom['distance'])
        print(restroom['distance'])
        r_id = restroom['id']
        querySet = Restroom.objects.filter(yelp_id=r_id)
        if not querySet:
            restroom['our_rating'] = 'no rating'
            restroom['db_id'] = ''
        else:
            restroom['our_rating'] = querySet.values()[0]['rating']
            restroom['db_id'] = querySet.values()[0]['id']
            print(restroom['db_id'])
        addr = str(restroom['location']['display_address'])
        restroom['addr'] = addr.translate(str.maketrans('', '', '[]\''))

    context['form'] = form
    context['location'] = location
    context['data'] = data
    return render(request, "naturescall/search_restroom.html", context)


# The page for adding new restroom
def add_restaurant(request, r_id):
    if request.method== 'POST':
        f= AddRestroom(request.POST)
        if f.is_valid():
            post= f.save(commit= False)
            post.save()
            return HttpResponseRedirect(reverse('naturescall:index'))
        else:
            return render(request, "naturescall/add_restaurant.html", {'form':f})
    else:
        k= get_business(api_key, r_id)
        context={}
        name= k['name']
        form = AddRestroom(initial= {'yelp_id' : r_id})
        context['form']= form
        context['name']= name
        return render(request, "naturescall/add_restaurant.html", context)


# The page for showing a single restroom detail
def restroom_detail(request, r_id):
    """Show a single restroom"""
    querySet = Restroom.objects.filter(id=r_id)
    res = {}
    if querySet:
        yelp_id = querySet.values()[0]['yelp_id']
        yelp_data = get_business(api_key, yelp_id)
        yelp_data['db_id'] = r_id
        yelp_data['rating'] = querySet.values()[0]['rating']
        yelp_data['Accessible'] = querySet.values()[0]['Accessible']
        yelp_data['FamilyFriendly'] = querySet.values()[0]['FamilyFriendly']
        yelp_data['TransactionRequired'] = querySet.values()[0]['TransactionRequired']

        res['yelp_data'] = yelp_data
        addr = str(yelp_data['location']['display_address'])
        res['addr'] = addr.translate(str.maketrans('', '', '[]\''))
        res['desc'] = querySet.values()[0]['Description']

    context = {'res': res}
    return render(request, "naturescall/restroom_detail.html", context)


# Helper function: make a request to the API
def request(host, path, api_key, url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }
    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()


# Helper function: fetch Yelp business data according to the term, location and the number of businesses
def search(api_key, term, location, num):
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': num,
        'radius': 500
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


# Helper function: fetch one specific Yelp business using the business_id
def get_business(api_key, business_id):
    business_path = BUSINESS_PATH + business_id
    return request(API_HOST, business_path, api_key)


# Helper function: getter for restroom property 'distance'
def getDistance(restroom_dic):
    return restroom_dic['distance']
