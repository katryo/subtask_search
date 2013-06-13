import requests
from pyquery import PyQuery as pq
from ad import Ad
from web_item import WebItem


class WebPage(WebItem):
    def __init__(self, url):
        response = requests.get(url)
        self.html = response.text

    def pick_something(self):
        text = pq(self.html).find('td>a>font').text()
        words = text.split(' ')
        normalized_words = []
        for word in words:
            word = word.lower()
            word = word.replace('_', '-')
            word = '"' + word + '",'
            normalized_words.append(word)
        return normalized_words

    def fetch_ads(self):
        nlist = pq(self.html).find('.nlist')
        lis = nlist.children().children()
        ads = []
        for li in lis:
            pq_li = pq(li)
            title = pq_li.find('a').text()
            link = pq_li.find('a').attr('href')
            snippet = pq_li.find('.yschabstr').text()
            ad_info = {'title': title, 'snippet': snippet, 'link': link}
            ad = Ad(ad_info)
            ads.append(ad)
        return ads
