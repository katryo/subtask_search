#coding: utf-8
from bottle import Bottle, route, run, static_file, request
from mako.template import Template
from search_engine import SearchEngine
from query_converter import Converter
from scraper import Scraper
import pdb


template = Template(filename='static/templates/index.tmpl')
app = Bottle()


@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')


@route('/results')
def results_get():
    return template.render(items='')


@route('/results', method='POST')
def results():
    query = request.forms.decode().get('query')
    search_engine = request.forms.get('search_engine')
    keywords = Converter.split_janapese_query(query)
    query = ' '.join(keywords)
    if search_engine == 'google':
        items = SearchEngine.google_search(query)
        results = []
        words = [
            'を使う', 'しましょう', 'ください', '下さい', 'がおすすめ', 'がオススメ',
            'を選ぶ'
        ]
        for item in items:
            link_and_texts = Scraper.find_word(item['link'], words)
            link_and_texts['title'] = item['title']
            if link_and_texts['texts'] == []:
                continue
            else:
                results.append(link_and_texts)
        return template.render(items=results)
    elif search_engine == 'bing':
        items = SearchEngine.bing_search(query)
    return template.render(items=items)


@route('/')
def greet():
    return template.render(items='')
run(host='localhost', port=1234, debug=True)
