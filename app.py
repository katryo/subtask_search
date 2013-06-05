#coding: utf-8
from bottle import Bottle, route, run, static_file, request
from mako.template import Template
from search_engine import SearchEngine
from query_converter import Converter
from scraper import Scraper
import requests
from urllib.parse import urljoin
import pdb


template = Template(filename='static/templates/index.tmpl')
sponsered_add_template = Template(filename='static/templates/sponsered_ad_template.tmpl')
app = Bottle()


@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')


@route('/yahoo_sponsored_results')
def yahoo_sponsored_results():
    query = request.forms.decode().get('query')
    head = 'http://search.yahoo.co.jp/search/ss?p='
    tail = '&ei=UTF-8&fr=top_ga1_sa&type=websearch&x=drt'
    url = head + query + tail
    scraper = Scraper(url)
    items = scraper.find_ad_texts()
    return sponsered_add_template.render(items=items)


@route('/results')
def results_get():
    return template.render(items='')

@route('/results', method='POST')
def results():
    query = request.forms.decode().get('query')
    search_engine = request.forms.get('search_engine')
    keywords = Converter.split_janapese_query(query)
    query = ' '.join(keywords)
    engine = SearchEngine()
    if search_engine == 'google':
        items = engine.google_search(query)
    elif search_engine == 'bing':
        items = engine.bing_search(query)

    results = []
    words = [
        'を使う', 'しましょう', 'てください', 'でください', 'で下さい', 'て下さい',
        'がおすすめ', 'がオススメ', '有効',
        'を選ぶ', 'してみては', 'するのがいい', 'するのがよい', 'するのが良い'
    ]
    for item in items:
        scraper = Scraper(item['link'])
        link_and_texts = scraper.find_words(words)
        link_and_texts['title'] = item['title']
        if link_and_texts['texts'] == []:
            continue
        else:
            results.append(link_and_texts)

    return template.render(items=results)


@route('/')
def greet():
    return template.render(items='')
run(host='localhost', port=1234, debug=True)
