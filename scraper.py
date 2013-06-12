import pdb
import MeCab
from pyquery import PyQuery as pq
import urllib.robotparser
from urllib.parse import urljoin
import requests
import re
import cgi
from constants import Constants
from analyzer import Analyzer  # scraperからanalyzer参照する。逆はしない
from mecabed_word import MecabedWord


class Scraper:
    def to_texts(self, items):
        m_word_collection = []
        analyzer = Analyzer()
        for item in items:
            html = self.fetch_html(item['link'])
            text = re.sub('<[^<]+?>', '', html)
            text = re.sub('(,|\.|#|\"|\/|:|{|})', '', text)
            m_words = analyzer.to_m_words(text)
            m_word_collection.extend(m_words)
        task_words = []
        for m_word in m_word_collection:
            if m_word.type == '動詞' or m_word.subtype == 'サ変接続':
                task_words.append(m_word.name)
        results = analyzer.to_ranked_items(task_words)
        return results

    def fetch_title_vs(self, url):
        items = self.fetch_ads(url)
        verbs = []
        sahens = []
        analyzer = Analyzer()
        for item in items:
            verbs.extend(analyzer.pick_verbs(item['title']))
            sahens.extend(analyzer.pick_sahens(item['title']))
        results = verbs + sahens
        return results

    def fetch_snippets_nvs(self, url):
        items = self.fetch_ads(url)
        nouns = []
        verbs = []
        sahens = []
        analyzer = Analyzer()
        for item in items:
            snippet_nouns = analyzer.pick_nouns(item['snippet'])
            snippet_verbs = analyzer.pick_verbs(item['snippet'])
            snippet_sahens = analyzer.pick_sahens(item['snippet'])
            nouns.extend(snippet_nouns)
            verbs.extend(snippet_verbs)
            sahens.extend(snippet_sahens)

        nvs = {'nouns': nouns, 'verbs': verbs, 'sahens': sahens}
        return nvs

    def fetch_ad_pages_nvs(self, url):
        texts = self.fetch_ad_pages(url)
        nouns = []
        verbs = []
        sahens = []
        analyzer = Analyzer()
        for text in texts:
            nouns.extend(analyzer.pick_nouns(text))
            verbs.extend(analyzer.pick_verbs(text))
            sahens.extend(analyzer.pick_sahens(text))
        nvs = {'nouns': nouns, 'verbs': verbs, 'sahens': sahens}
        return nvs

    def fetch_ad_pages(self, url):
        items = self.fetch_ads(url)
        texts = []
        words = Constants.TASK_WORDS
        for item in items:
            texts_in_one_page = self.find_words(words, item['link'])
            #texts_in_one_page => ['水がおすすめ', '気をつけてください']
            texts.extend(texts_in_one_page)
        #texts => ['!!! 気をつけてください !!!', 'ここをクリックして新製品を使う', '深呼吸してみては']
        return texts

    def fetch_html(self, url):
        response = requests.get(url)
        html = response.text
        return html

    def fetch_something(self, url):
        response = requests.get(url)
        html = response.text
        text = pq(html).find('td>a>font').text()
        words = text.split(' ')
        normalized_words = []
        for word in words:
            word = word.lower()
            word = word.replace('_', '-')
            word = '"' + word + '",'
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
            ad_snippet = pq_li.find('.yschabstr').text()
            item = {'title': ad_title, 'snippet': ad_snippet, 'link': link}
            items.append(item)
        return items

    def pick_vs(self, url):
        response = requests.get(url)
        text = response.text
        analyzer = Analyzer()
        verbs = analyzer.pick_verbs(text)
        sahens = analyzer.pick_sahens(text)
        results = verbs + sahens
        return results


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
        return matched_texts
