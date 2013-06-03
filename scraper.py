import pdb
import MeCab
from pyquery import PyQuery as pq
import requests
import re
import cgi


class Scraper:
    def find_word(url, words):
        response = requests.get(url)
        txt = response.text
        matched_texts = []
        black_words = [
            'ログイン', 'サインイン', 'カート', '検索キーワード', '検索したい単語',
            'javascript', 'JavaScript', 'Javascript',
            'ボタンを押してください', '勝利馬券をゲット', '教えて', '助けて', '責任',
            'ご覧ください', 'JAPAN ID', '入力して', '無断転載', 'リンクを参照'
        ]
        for word in words:
            pattern = re.compile(word)
            matches = pattern.finditer(txt)
            for match in matches:
                end_point = match.end()
                start_point = end_point - len(word)
                matched_text = txt[start_point - 30:end_point]
                black_word_found = False
                for black_word in black_words:
                    if black_word in matched_text:
                        black_word_found = True
                        continue
                if black_word_found == True:
                    continue
                else:
                    matched_text = cgi.escape(matched_text, quote=True)
                    matched_texts.append(matched_text)
        link_and_texts = {'link': url, 'texts': matched_texts}
        return link_and_texts
