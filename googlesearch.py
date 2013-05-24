import urllib
import urllib.request
import urllib.parse
import json
import pdb


def simple_search(query):
    QUERY = query
    API_KEY = 'AIzaSyBdhBTUc5W5Aco3YGPwOlS_rYM0LBKl_jo'
    NUM = 1

    url = 'https://www.googleapis.com/customsearch/v1?'
    params = {
        'key': API_KEY,
        'q': QUERY,
        'cx': '013036536707430787589:_pqjad5hr1a',
        'alt': 'json',
        'lr': 'lang_ja', }
    start = 1
    items = []

    for i in range(0, NUM):
        params['start'] = start
        request_url = url + urllib.parse.urlencode(params)
        try:
            response = urllib.request.urlopen(request_url)
            json_body = json.loads(response.read().decode('utf-8'))
            items.append(json_body['items'])
            if not 'nextPage' in json_body['queries']:
                break
            start = json_body['queries']['nextPage'][0]['startIndex']
        except:
            print('Error')

    return items
