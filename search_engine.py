import urllib
import urllib.request
import urllib.parse
import json
import pdb
import my_keys
import constants
import requests


class SearchEngine:
    def __init__(self):
        self.microsoft_api_key = my_keys.MICROSOFT_API_KEY
        self.google_api_key = my_keys.GOOGLE_API_KEY

    def google_search(self, query, num):
        NUM = num
        url = 'https://www.googleapis.com/customsearch/v1?'
        params = {
            'key': self.google_api_key,
            'q': query,
            'cx': '013036536707430787589:_pqjad5hr1a',
            'alt': 'json',
            'lr': 'lang_ja',
        }
        start = 1
        items = []

        for i in range(0, NUM):
            params['start'] = start
            request_url = url + urllib.parse.urlencode(params)
            try:
                response = urllib.request.urlopen(request_url)
                json_body = json.loads(response.read().decode('utf-8'))
                items.extend(json_body['items'])
                if not 'nextPage' in json_body['queries']:
                    break
                start = json_body['queries']['nextPage'][0]['startIndex']
            except:
                items.extend({'link': '#', 'title': '検索できませんでした'})
        return items  #=> [{'link': 'http://...', 'title': 'ページは'}, {...}...]

    def bing_search(self, query):
        NUM = 1
        key = self.microsoft_api_key
        url = 'https://api.datamarket.azure.com/Bing/Search/Web?'
        json_param = '&$format=json'
        param = {
            'Query': "'" + query + "'",
        }
        req_url = url + urllib.parse.urlencode(param)
        items = []

        for i in range(0, NUM):
            try:
                json_body = requests.get(req_url + json_param, auth=(key, key)).json()
                items.extend(json_body['d']['results'])
                req_url = json_body['d']['__next']
            except:
                items.extend({'Url': '#', 'Title': '検索できませんでした'})

        for item in items:
            item['link'] = item['Url']
            item['title'] = item['Title']

        return(items)
