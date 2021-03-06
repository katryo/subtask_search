#coding: utf-8
from bottle import Bottle, route, run, static_file, request
from search_engine import SearchEngine
from jinja2 import Environment, FileSystemLoader
from web_page import WebPage
from web_item import WebItem
import pdb

env = Environment(loader=FileSystemLoader('static/templates'))
template = env.get_template('index.tmpl')
results_template = env.get_template('results.tmpl')
sahen_google_template = env.get_template('sahen_google.tmpl')
expand_template = env.get_template('expand.tmpl')
ad_template = env.get_template('ad.tmpl')
free_scraping_template = env.get_template('free.tmpl')
app = Bottle()


@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')


@route('/yahoo_sponsored_results', method='POST')
def yahoo_sponsored_results():
    query = request.forms.decode().get('query')
    #yahooスポンサードサーチは単語ごとに区切るより一文にしたほうが広告出やすい
    head = 'http://search.yahoo.co.jp/search/ss?p='
    tail = '&ei=UTF-8&fr=top_ga1_sa&type=websearch&x=drt'
    url = head + query + tail
    y_ad_page = WebPage(url)
    ads = y_ad_page.fetch_ads()
    v_and_s = []
    for ad in ads:
        v_and_s.extend(ad.pick_verbs(ad.title))
        v_and_s.extend(ad.pick_sahens(ad.title))
        v_and_s.extend(ad.pick_verbs(ad.snippet))
        v_and_s.extend(ad.pick_sahens(ad.snippet))
    results = to_ranked_items(v_and_s)
    return ad_template.render(items=results)


def to_ranked_items(items):
    rank_dict = {}
    #items => ['対策', '鼻炎', '対策', 'うるおい', ...]
    for item in items:
        if item in rank_dict.keys():
            rank_dict[item] += 1
        else:
            rank_dict[item] = 1
    #rank_dict => {'対策': 2, '鼻炎': 1, ...}
    keys = rank_dict.keys()  # => ['対策', '鼻炎', ...]
    results = []
    for key in keys:
        count = rank_dict[key]  # => 2
        result = {'name': key, 'count': count}
        results.append(result)
    #results => [{'name': '対策', 'count': 2},  ....]
    outputs = divide_by_count(results)
    return outputs


def divide_by_count(items):
    high_items = []
    middle_items = []
    low_items = []
    for item in items:
        if item['count'] > 2:
            high_items.append(item)
        elif item['count'] == 2:
            middle_items.append(item)
        else:
            low_items.append(item)
    outputs = []
    outputs.extend(high_items)
    outputs.extend(middle_items)
    outputs.extend(low_items)
    return outputs


@route('/results')
def results_get():
    return template.render(items='')


@route('/query_expansion', method='post')
def query_expansion():
    query = request.forms.decode().get('query')
    #yahooスポンサードサーチは単語ごとに区切るより一文にしたほうが広告出やすい
    head = 'http://search.yahoo.co.jp/search/ss?p='
    tail = '&ei=UTF-8&fr=top_ga1_sa&type=websearch&x=drt'
    url = head + query + tail
    y_ad_page = WebPage(url)
    ads = y_ad_page.fetch_ads()
    v_and_s = []
    for ad in ads:
        v_and_s.extend(ad.pick_verbs(ad.title))
        v_and_s.extend(ad.pick_sahens(ad.title))
        v_and_s.extend(ad.pick_verbs(ad.snippet))
        v_and_s.extend(ad.pick_sahens(ad.snippet))
    ranked_items = to_ranked_items(v_and_s)
    ranked_items.insert(0, {'name': 'まとめ', 'count': 100})
    normalized_query = normalize_query(query)
    query_words = normalized_query.split(' ')
    page_set = set()  # set型は重複をなくすため
    expanded_queries = []
    for item in ranked_items:
        top_5 = []
        if item['name'] in query_words:
            #'花粉症 対策'で検索したら'対策'がitem['name']に入っていたりする
            continue
        else:
            expanded_query = normalized_query + ' ' + item['name']
            expanded_queries.append(expanded_query)
            new_pages = search(expanded_query, 1)
            top_5 = new_pages[0:4]
        over_19 = False
        for one in top_5:
            page_set.add(one)
            if len(page_set) > 19:
                over_19 = True
                break
        if over_19 is True:
            break  # => ranked_items内で回すのから脱出
    return expand_template.render(pages=page_set, queries=expanded_queries)


def search(query, count):
    search_engine = request.forms.get('search_engine')
    engine = SearchEngine()
    if search_engine == 'google':
        pages = engine.google_search(query, count)
    elif search_engine == 'bing':
        pages = engine.bing_search(query, count)
    return pages


def normalize_query(query):
    web_item = WebItem()
    keywords = web_item.pick_nouns_and_verbs(query)
    normalized_query = ' '.join(keywords)
    return normalized_query


@route('/results', method='POST')
def results():
    query = request.forms.decode().get('query')
    normalized_query = normalize_query(query)
    pages = search(normalized_query, 1)
    v_and_s = []
    for page in pages:
        v_and_s.extend(page.pick_verbs(page.title))
        v_and_s.extend(page.pick_sahens(page.title))
        v_and_s.extend(page.pick_verbs(page.snippet))
        v_and_s.extend(page.pick_sahens(page.snippet))
    results = to_ranked_items(v_and_s)
    return sahen_google_template.render(items=results)


@route('/free_scraping_results', method='POST')
def free_scraping_results():
    url = request.forms.decode().get('url')
    page = WebPage(url)
    items = page.pick_something()
    return free_scraping_template.render(items=items)


@route('/')
def index():
    return template.render()
run(host='localhost', port=1234, debug=True)
