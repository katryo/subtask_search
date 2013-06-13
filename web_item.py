from mecabed_word import MecabedWord
import MeCab


class WebItem:
    def pick_words_by_types(self, str, types):
        keywords = []
        m_words = self.to_m_words(str)
        for m_word in m_words:
            for type in types:
                if m_word.type == type:
                    keywords.append(m_word.name)
        return keywords

    def pick_words_by_type(self, str, type):
        types = [type]
        keywords = self.pick_words_by_types(str, types)
        return keywords

    def pick_sahens(self, str):
        keywords = []
        m_words = self.to_m_words(str)
        for m_word in m_words:
            if m_word.subtype == 'サ変接続':
                item = m_word.name
                keywords.append(item)
        return keywords

    def pick_verbs(self, str):
        keywords = self.pick_words_by_type(str, '動詞')
        return keywords

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

    def pick_nouns_and_verbs(self, str):
        types = ['名詞', '動詞']
        keywords = self.pick_words_by_types(str, types)
        return keywords
