from django.shortcuts import render
from django.http import HttpResponse
from .forms import LocationForm
import requests
import argparse
import json
import sys
import urllib
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode
api_key = 'CL1ez7IjEGAsK5LINl-ehN8lTuQSaOqP8NncZD0e8JRLcOmmACCc3u87rtD7l1Bwpc9uzwQF8Oj2K6lo7f9cHo2P6xhlCFSI6Thph0MaRgRDcM4XA6iww7AX8QROYXYx'
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'
DEFAULT_TERM = 'food'
SEARCH_LIMIT = 3

def index(request):
    context={}
    form= LocationForm(request.POST or None)
    context['form']= form
    return render(request, "naturescall/index.html", context)
def yelpSearch(request):
    context={}
    form= LocationForm(request.POST or None)
    location = request.POST['location']
    k= search(api_key,DEFAULT_TERM, location)
    data=[]
    if not k.get('error'):
        data= k['businesses']
    print(data)
    context['form']= form
    context['location']= location
    context['data']= data
    print(request.POST)
    return render(request, "naturescall/yelpSearch.html", context)

def request(host, path, api_key, url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
            'Authorization': 'Bearer %s' % api_key,
            }
    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()
def search(api_key, term, location):
    url_params = {
            'term': term.replace(' ', '+'),
            'location': location.replace(' ', '+'),
            'limit': SEARCH_LIMIT
            }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)
def get_business(api_key, business_id):
    business_path = BUSINESS_PATH + business_id
    return request(API_HOST, business_path, api_key)