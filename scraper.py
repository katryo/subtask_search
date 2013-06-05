import pdb
import MeCab
from pyquery import PyQuery as pq
import urllib.robotparser
import requests
import re
import cgi


class Scraper:
    def __init__(self, url):
        self.url = url
        self.rp = urllib.robotparser.RobotFileParser()

    def find_ad_texts(self):
        response = requests.get(self.url)
        html = response.text
        nlist = pq(html).find('.nlist')
        lis = nlist.children().children()
        items = []
        for li in lis:
            pq_li = pq(li)
            ad_title = pq_li.find('a').text()
            ad_text = pq_li.find('.yschabstr').text()
            link = pq_li.find('em').text()
            item = {'ad_title': ad_title, 'ad_text': ad_text, 'link': link}
            items.append(item)

        return items

    def find_words(self, words):
        response = requests.get(self.url)
        txt = response.text
        matched_texts = []
        black_words = [
            'ログイン', 'サインイン', 'カート', '検索キーワード', '検索したい単語',
            'javascript', 'JavaScript', 'Javascript',
            'ボタンを押してください', '勝利馬券をゲット', '教えて', '助けて', '責任',
            'ご覧ください', 'JAPAN ID', '入力して', '無断転載', 'リンクを参照', '回答',
            'ノートに戻り、もう一度やり直してください', 'ページで登録されているノートを削除してください',
            'プレビューボタン', '注文手続きの際にお申し込み', 'Kindle化をご希望の場合',
            '</ul> <br /> <strong> 必ずお読みください', 'エラーが発生しました。やり直してください',
            '>もう一度試してください', '意見交換を通じて、お買い物にお役立てください',
            'Amazon.co.jp</a></b> が販売、発送します',
            'この機能は現在利用できません。しばらくしてからもう一度お試しください',
            '不適切な項目が含まれていることもあります。ご了承ください',
            'このユーザーのブロックを解除します', 'このユーザーをブロックします',
            '呼び出しを適切な位置に挿入してください',
            'このタグを +1 ボタンを表示する場所に挿入してください',
            '参考にしてみてください',
            'このトピックについて、他の呼び方、通称などがあれば登録してください',
            'メモやコメントの追加はここをクリックして下さい',
            'ノート</a>を参照してください',
            'この操作を実行するには、プライバシー設定を変更してください',
            '利用規約</a>を参照してください',
            'メニューを入れてください',
            'エリア、都道府県を選択してください',
            '観光地を選択してください'
        ]
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
        link_and_texts = {'link': self.url, 'texts': matched_texts}
        return link_and_texts
