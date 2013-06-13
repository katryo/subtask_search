import requests
from constants import Constants
from web_item import WebItem


class Ad(WebItem):
    def __init__(self, args={'title': '', 'snippet': '', 'link': ''}):
        self.title = args['title']
        self.snippet = args['snippet']
        self.link = args['link']
        #linkは広告のWebページURLではなくyahooのURLを経由

    def fetch_html(self):
        response = requests.get(self.link)
        #linkはyahooのURLだがレスポンスは広告元のページ
        self.html = response.text

    def fetch_ad_pages(self):
        words = Constants.TASK_WORDS
        self.texts = self.find_words(words, self.link)
        #texts => ['水がおすすめ', '気をつけてください']
