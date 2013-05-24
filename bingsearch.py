import urllib
import urllib.request
import urllib.parse
import json
import requests
import pdb


def simple_search(query):
    NUM = 1
    key = 'd8UCcfqGTiuke8wAxdnI0wDG4W0GLQSbC37NjI1K9lca8'
    url = 'https://api.datamarket.azure.com/Bing/Search/Web?'
    json_param = '&$format=json'
    param = {
        'Query': "'" + query + "'",
    }
    req_url = url + urllib.parse.urlencode(param)
    items = []

    for i in range(0, NUM):
        json_body = requests.get(req_url + json_param, auth=(key, key)).json()
        items.append(json_body['d']['results'])
        req_url = json_body['d']['__next']
    return(items)
