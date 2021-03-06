#!/usr/bin/env python
from __future__ import print_function
from elasticsearch.client import IndicesClient
from elasticsearch import Elasticsearch,RequestsHttpConnection
from future.standard_library import install_aliases
install_aliases()
from flask import Flask
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import json
import os
from flask import request
from flask import make_response
import argparse
import pprint
import requests
import sys
import urllib
para = 0

host = 'search-foodbot-eho7uxotx6zjwcdwclacvre7ni.us-west-2.es.amazonaws.com'
port = 443
ES_CLIENT = Elasticsearch(
        hosts=[{'host': host,'port':port}],
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
        )
indices_client = IndicesClient(client=ES_CLIENT)
i=1

# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


# OAuth credential placeholders that must be filled in by users.
# You can find them on
# https://www.yelp.com/developers/v3/manage_app
CLIENT_ID = "NZ-KxOMeY2CqaQb4mrOH4Q"
CLIENT_SECRET = "gJ2KlV2nozjCcvJ0w1Pz9rs23Zz1JwTlvzfJ4emQCdayZmkoB7WfeJP6p79M6Exa"


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'


# Defaults for our simple example.
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT =  4


# Flask app should start in global layout
app = Flask(__name__)
@app.route('/')
def hello():
    result=make_response("Hello")
    return result
@app.route('/webhook', methods=['POST','GET'])
def webhook():
    req = request.get_json(silent=True, force=True)
    ac=req.get("result").get("action")
    my_previous_action=req.get("result").get("parameters").get("my-action")
    if ac=="restname":
        n= req.get("result").get("parameters").get("rest")
        es = Elasticsearch(hosts=[{'host': host,'port':port}],use_ssl=True,verify_certs=True,connection_class=RequestsHttpConnection)
        res = es.search(size=10,index="fb", body={"query": {"match":{"name":n}}})      
    #res = es.get(index="fb")
        listOfDicts = []
        listOfRating=[]
        listOfImage= []
        for idx in range(len(res['hits']['hits'])):
            sourceValue = res['hits']['hits'][idx]['_source']
            text=sourceValue['name']
            listOfRating.append(sourceValue['rating'])
            listOfImage.append(sourceValue)
            listOfDicts.append(''.join([i if ord(i) < 128 else '' for i in text])) 
        res =makeWebhookResult1(listOfImage)   # print (listOfDicts)
        res=json.dumps(res,indent=4)
        res=make_response(res)
        res.headers['Content-Type'] = 'application/json'
        return res

    elif ac=="previousContext":
        #ac=my_previous_action
        #place=req.get("result").get("parameters").get("geo-city")
        global para
        para = req.get("result").get("parameters").get("myparam")
        #if req1.get("result").get("parameters").get("geo-city"):
        loc=req.get("result").get("parameters").get("geo-city")
        print (req)
        req=req["result"]["parameters"].get("Cuisine")
        #else:
            #loc=req1.get("result").get("parameters").get("geo-state-us")



    elif ac=="previousContext1":
        res=json.dumps(
        {
        "speech": "What do you want to filter according to, rating or price?",
        "displayText": "what do you want to fiter according to, rating or price? ",
        # "data": data,
        # "contextOut: [],
        "source": "Yelp"
        },indent=4)
        res=make_response(res)
        res.headers['Content-Type'] = 'application/json'
        return res

        
    elif ac == "another":
        res=json.dumps(
        {
        "speech": "Can you specify the location?",
        "displayText": "Can you specify the location?",
        # "data": data,
        # "contextOut: [],
        "source": "Yelp"
        },indent=4)
        res=make_response(res)
        res.headers['Content-Type'] = 'application/json'
        return res





    else :
       # place=req.get("result").get("parameters").get("geo-city")
        req=req.get("result").get("parameters").get("Cuisine")

    

    # print (req)
    es = Elasticsearch(hosts=[{'host': host,'port':port}],use_ssl=True,verify_certs=True,connection_class=RequestsHttpConnection)
    res = es.searchres = es.search(size=10,index="fb", body={"query" : {
            "bool" : {
                "must" : [
                    { "match" : {"type" : req}}, 
                    { "match" : {"location" : loc}}]
        } }})
    print (len(res['hits']['hits']))
    print(req)
    print(loc)      
    #res = es.get(index="fb")
    listOfDicts = []
    listOfRating=[]
    listOfImage=    []
    for idx in range(len(res['hits']['hits'])):
        sourceValue = res['hits']['hits'][idx]['_source']
        text=sourceValue['name']
        listOfRating.append(sourceValue['rating'])
        listOfImage.append(sourceValue)
        listOfDicts.append(''.join([i if ord(i) < 128 else '' for i in text]))
    if para!=0:
        if para=='rating':
            criterion=True
        else:
            criterion=False
        listOfImage=sorted(listOfImage,key=lambda key:key[para],reverse=criterion)
  

    if ac=="rating":
        res =makeWebhookResult1(listOfImage)
    elif ac=="address":
        res = makeWebhookResult2(listOfImage)
    elif ac=="display":
        res = makeWebhookResult(listOfImage)
    elif ac=="previousContext":
        res=makeWebhookResult(listOfImage)
    else:
        res=makeWebhookResult(listOfImage)

    # res=json.dumps(res,indent=4)
    # r = make_response(res)
    # r.headers['Content-Type'] = 'application/json'
    # return r
    # return json.dumps(listOfDicts)
    # res=makeWebhookResult()
    res=json.dumps(res,indent=4)
    res=make_response(res)
    res.headers['Content-Type'] = 'application/json'
    return res


def processRequest(req):
    """if req.get("result").get("action") != "yahooWeatherForecast":
                    return {}"""
    """baseurl = "https://query.yahooapis.com/v1/public/yql?"
                yql_query = makeYqlQuery(req)
                if yql_query is None:
                    return {}
                yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
                result = urlopen(yql_url).read()
                data = json.loads(result)"""
   	#req.get("result").get("action") == "rating":
    res=query_api(req.get("result").get("parameters").get("Cuisine"),"NY")
    z = makeWebhookResult1(res)
    return z
    # elif req.get("result").get("action") == "restaurants":
    #     res=query_api(req.get("result").get("parameters").get("Cuisine"),"NY")
    #     z = makeWebhookResult(res)
    #     return z



def makeWebhookResult2(data1):
    if data1 and len(data1)>0:
        speech= "Here is the list"
    else :
        return {'speech':'Sorry I could not come up with restaurants at this time',
        "displayText":'Sorry I could not come up with restaurants at this time',
        'source':'API'}
    location="http://maps.google.com/?q="
    dict_of_elements=[]
    for i in data1:
        ducs={}
        ducs['title']=i['name']
        ducs['image_url']=i['image_url']
        ducs['subtitle']="Price:"+str(i['price'])+'\tRating:'+str(i['rating'])
        new={}
        new['type']='web_url'
        new['url']=i['url']
        new['title']='View website'
        newPhone={}
        newPhone['type']='phone_number'
        newPhone['payload']=i['phone']
        newPhone['title']='Call'
        newList=[]
        #mapOpener['payload']=location+''.join(str(x) for x in i['location']).replace(' ','+')
        newList.append(new)
        newList.append(newPhone)
        #newList.append(mapOpener)
        ducs['buttons']=newList
        dict_of_elements.append(ducs)

    return {'speech':speech,
        "displayText":speech,
        "data":{
        'facebook':{
        "attachment": {
        "type": "template",
        "payload": {
        "template_type": "generic",
        "elements": dict_of_elements
        }
        }
        }},
        'source':'Yelp'}

def makeWebhookResult1(data):
        
        dict_of_elements=[]
        for i in data:
            ducs={}
            ducs['title']=i['name']
            ducs['image_url']=i['image_url']
            ducs['subtitle']="Price:"+str(i['price'])+'    Rating'+str(i['rating'])
            new={}
            new['type']='web_url'
            new['url']=i['url']
            new['title']='View website'
            newPhone={}
            newPhone['type']='phone_number'
            newPhone['payload']=i['phone']
            newPhone['title']='Call'
            newList=[]
            #mapOpener['payload']=location+''.join(str(x) for x in i['location']).replace(' ','+')
            newList.append(new)
            newList.append(newPhone)
            #newList.append(mapOpener)
            ducs['buttons']=newList
            dict_of_elements.append(ducs)
        return {'speech':"Here is a list",
            "displayText":"Here is a list",
            "data":{
            'facebook':{
            "attachment": {
            "type": "template",
            "payload": {
            "template_type": "generic",
            "elements": dict_of_elements
            }
            }
            }},
        'source':'API'}
        


def makeWebhookResult(data):
    if data and len(data)>0:
        speech= "Here is the list"
    else :
        return {'speech':'Sorry I could not come up with restaurants at this time',
        "displayText":'Sorry I could not come up with restaurants at this time',
        'source':'API'}
    dict_of_elements=[]
    for i in data:
        ducs={}
        ducs['title']=i['name']
        ducs['image_url']=i['image_url']
        ducs['subtitle']="Price:"+str(i['price'])+'    Rating'+str(i['rating'])
        new={}
        new['type']='web_url'
        new['url']=i['url']
        new['title']='View website'
        newPhone={}
        newPhone['type']='phone_number'
        newPhone['payload']=i['phone']
        newPhone['title']='Call'
        newList=[]
        #mapOpener['payload']=location+''.join(str(x) for x in i['location']).replace(' ','+')
        newList.append(new)
        newList.append(newPhone)
        #newList.append(mapOpener)
        ducs['buttons']=newList
        dict_of_elements.append(ducs)

    return {'speech':"Here is a list",
        "displayText":"Here is a list",
        "data":{
        'facebook':{
        "attachment": {
        "type": "template",
        "payload": {
        "template_type": "generic",
        "elements": dict_of_elements
        }
        }
        }},
        'source':'Yelp'}

def obtain_bearer_token(host, path):
    """Given a bearer token, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        str: OAuth bearer token, obtained using client_id and client_secret.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    assert CLIENT_ID, "Please supply your client_id."
    assert CLIENT_SECRET, "Please supply your client_secret."
    data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
    })
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    return bearer_token


def request_from_yelp(host, path, bearer_token, url_params=None):
    """Given a bearer token, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % bearer_token,
    }
    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()


def search(bearer_token, term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    lalal=request_from_yelp(API_HOST, SEARCH_PATH, bearer_token, url_params=url_params)
    return lalal


def get_business(bearer_token, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id
    return request_from_yelp(API_HOST, business_path, bearer_token)


def query_api(term, location):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)
    response = search(bearer_token, term, location)
    businesses = response.get('businesses')
    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return
    final_result=''
    for i in businesses:
        business_id = i['id']
        # print (business_id)
        # print(u'{0} businesses found, querying business info ' \
        # 'for the top result "{1}" ...'.format(
        #     len(businesses), business_id))
        response =get_business(bearer_token, business_id)
        # print(u'Result for business "{0}" found:'.format(business_id))
    #return ','.join([str(x['name']) for x in businesses])
    return businesses



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True)
