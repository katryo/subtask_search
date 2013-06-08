import pdb
import MeCab
from pyquery import PyQuery as pq
import urllib.robotparser
from urllib.parse import urljoin
import requests
import re
import cgi
from constants import Constants


class Scraper:
    def fetch_ad_texts(self, url):
        items = self.fetch_ads(url)
        results = []
        for item in items:
            words = Constants.TASK_WORDS
            link_and_texts = self.find_words(words, item['link'])
            link_and_texts['title'] = item['ad_title']
            results.append(link_and_texts)
        return results

    def fetch_something(self, url):
        response = requests.get(url)
        html = response.text
        text = pq(html).find('td>a>font').text()
        words = text.split(' ')
        normalized_words = []
        for word in words:
            word = word.lower()
            word = word.replace('_', '-')
            word = word + ','
            normalized_words.append(word)
        return normalized_words

    def fetch_ads(self, url):
        response = requests.get(url)
        html = response.text
        nlist = pq(html).find('.nlist')
        lis = nlist.children().children()
        items = []
        for li in lis:
            pq_li = pq(li)
            ad_title = pq_li.find('a').text()
            link = pq_li.find('a').attr('href')
            ad_text = pq_li.find('.yschabstr').text()
            item = {'ad_title': ad_title, 'ad_text': ad_text, 'link': link}
            items.append(item)
        return items

    def find_words(self, words, url):
        response = requests.get(url)
        txt = response.text
        matched_texts = []
        black_words = Constants.BLACK_WORDS
        break_words = [
            '。', '<p>', '<br />', '<br>'
        ]
        for word in words:
            pattern = re.compile(word)
            matches = pattern.finditer(txt)
            for match in matches:
                end_point = match.end()
                start_point = end_point - len(word)
                matched_text = txt[start_point - 50:end_point]
                for break_word in break_words:
                    dot_index = matched_text.rfind(break_word)
                    matched_text = matched_text[dot_index + len(break_word):]

                black_word_found = False
                for black_word in black_words:
                    if black_word in matched_text:
                        black_word_found = True
                        continue
                if black_word_found is True:
                    continue
                else:
                    tag_pattern = re.compile('<.*?>')
                    matched_text = tag_pattern.sub('', matched_text)
                    broken_tag_pattern = re.compile('.*>')
                    matched_text = broken_tag_pattern.sub('', matched_text)
                    escaped_broken_tag_pattern = re.compile('&quot;')
                    matched_text = escaped_broken_tag_pattern.sub('', matched_text)

                    matched_text = cgi.escape(matched_text, quote=True)
                    matched_texts.append(matched_text)
        link_and_texts = {'link': url, 'texts': matched_texts}
        return link_and_texts
