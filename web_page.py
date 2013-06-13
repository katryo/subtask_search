import requests
from pyquery import PyQuery as pq
from ad import Ad


class WebPage:
    def __init__(self, url):
        response = requests.get(url)
        self.html = response.text

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
