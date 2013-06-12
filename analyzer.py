import pdb
import re
import MeCab
import CaboCha
import xml.etree.ElementTree as etree
from mecabed_word import MecabedWord


class Analyzer:
    def to_ranked_items(self, items):
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
        outputs = self.divide_by_count(results)
        return outputs

    def divide_by_count(self, items):
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

    def to_m_words(self, str):
        tagger = MeCab.Tagger('mecabrc')
        result = tagger.parse(str)
        word_info_collection = result.split('\n')
        m_words = []
        for info in word_info_collection:
            #infoが',\t名詞,サ変接続,*,*,*,*,*'のようなときはbreakする
            if info == 'EOS' or info == '':
                break
            else:
                invalid = self.is_including_invalid_word(info)
                if invalid is True:
                    break
                else:
                    mw = MecabedWord(info)
                    #mw.name => '希望'
                    #mw.type => '名詞'
                    #mw.subtype => 'サ変接続'
                    m_words.append(mw)
        return m_words

    def is_including_invalid_word(self, info):
        head = info[0:4]
        invalid = False
        invalid_words = [
            ',', '.', '…', '(', ')', '-',
            '/', ':', ';', '&', '%', '％',
            '~', '〜', '≪', '≫', '[', ']',
            '|', '"'
        ]
        for invalid_word in invalid_words:
            if invalid_word in head:
                invalid = True
                break
        return invalid

    def to_chunks(self, str):
        parser = CaboCha.Parser()
        tree = parser.parse(str)
        xml_str = tree.toString(CaboCha.FORMAT_XML)
        root = etree.fromstring(xml_str)
        chunks = []
        for chunk in root:
            words = []
            link = chunk.get('link')
            for tok in chunk:
                words.append(tok.text)
            item = {'words': words, 'link': link}
            chunks.append(item)
        return chunks

    def pick_words_by_types(self, m_words, types):
        keywords = []
        for m_word in m_words:
            for type in types:
                if m_word.type == type:
                    keywords.append(m_word.name)
        return keywords

    def pick_words_by_type(self, query, type):
        words = self.to_m_words(query)
        types = [type]
        keywords = self.pick_words_by_types(words, types)
        return keywords

    def pick_nouns(self, query):
        keywords = self.pick_words_by_type(query, '名詞')
        return keywords

    def pick_sahens(self, str):
        m_words = self.to_m_words(str)
        keywords = []
        for m_word in m_words:
            if m_word.subtype == 'サ変接続':
                item = m_word.name
                keywords.append(item)
        return keywords

    def pick_verbs(self, str):
        keywords = self.pick_words_by_type(str, '動詞')
        return keywords

    def pick_nouns_and_verbs(self, str):
        words = self.to_m_words(str)
        types = ['名詞', '動詞']
        keywords = self.pick_words_by_types(words, types)
        return keywords
