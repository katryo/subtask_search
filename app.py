
#coding: utf-8
from bottle import Bottle, route, run, static_file, request
#from mako.template import Template
#from mako.lookup import TemplateLookup
from search_engine import SearchEngine
from analyzer import Analyzer
from converter import Converter
from jinja2 import Environment, FileSystemLoader
from scraper import Scraper
from constants import Constants
import requests
from urllib.parse import urljoin
import pdb

env = Environment(loader=FileSystemLoader('static/templates'))
template = env.get_template('index.tmpl')
results_template = env.get_template('results.tmpl')
sahen_google_template = env.get_template('sahen_google.tmpl')
ad_template = env.get_template('ad.tmpl')
free_scraping_template = env.get_template('free.tmpl')
#sponsered_add_template = Template(filename='static/templates/sponsered_ad_template.tmpl')
app = Bottle()


@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')


@route('/yahoo_sponsored_results', method='POST')
def yahoo_sponsored_results():
    query = request.forms.decode().get('query')
    converter = Converter()
    words = converter.split_janapese_query(query)
    converted_query = ''.join(words)
    head = 'http://search.yahoo.co.jp/search/ss?p='
    tail = '&ei=UTF-8&fr=top_ga1_sa&type=websearch&x=drt'
    url = head + converted_query + tail
    scraper = Scraper()
    title_vs = scraper.fetch_title_vs(url)
    snippet_nvs = scraper.fetch_snippets_nvs(url)
    pages_nvs = scraper.fetch_ad_pages_nvs(url)
    items = snippet_nvs['sahens'] + snippet_nvs['verbs'] + pages_nvs['sahens'] + pages_nvs['verbs'] + title_vs
    analyzer = Analyzer()
    ranked_items = analyzer.to_ranked_items(items)
    return ad_template.render(items=ranked_items)


@route('/results')
def results_get():
    return template.render(items='')


@route('/results', method='POST')
def results():
    query = request.forms.decode().get('query')
    search_engine = request.forms.get('search_engine')
    analyzer = Analyzer()
    keywords = analyzer.pick_nouns_and_verbs(query)
    query = ' '.join(keywords)
    engine = SearchEngine()
    if search_engine == 'google':
        items = engine.google_search(query, 1)
    elif search_engine == 'bing':
        items = engine.bing_search(query)
    words = get_snippet_and_title(items)
    results = analyzer.to_ranked_items(words)
    return sahen_google_template.render(items=results)


def get_snippet_and_title(items):
    analyzer = Analyzer()
    m_words = []
    for item in items:
        snippet = item['snippet']
        m_words.extend(analyzer.pick_verbs(snippet))
        m_words.extend(analyzer.pick_sahens(snippet))
        title = item['title']
        m_words.extend(analyzer.pick_verbs(title))
        m_words.extend(analyzer.pick_sahens(title))
    return m_words  # => ['旅行', '対策', 'する']


def to_link_texts_title(items):
    results = []
    words = Constants.TASK_WORDS
    for item in items:
        scraper = Scraper()
        texts = scraper.find_words(words, item['link'])
        if texts == []:
            continue
        else:
            page = {'link': item['link'], 'texts': texts, 'title': item['title']}
            results.extend(page)
    return results


@route('/free_scraping_results', method='POST')
def free_scraping_results():
    url = request.forms.decode().get('url')
    scraper = Scraper()
    items = scraper.fetch_something(url)
    return free_scraping_template.render(items=items)


@route('/')
def greet():
    return template.render()
run(host='localhost', port=1234, debug=True)
