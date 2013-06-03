import pdb
import MeCab

#日本語の形態素解析をする
#splitする
#動詞と名詞だけでキーワードクエリにする


class Converter:
    def split_janapese_query(query):
        tagger = MeCab.Tagger('mecabrc')
        result = tagger.parse(query)
        words = result.split('\n')
        keywords = []
        for word in words:
            if word == 'EOS':
                break
            else:
                keyword_and_category = word.split(',')[0].split('\t')
                category = keyword_and_category[1]
                if category == '名詞' or category == '動詞':
                    keywords.append(keyword_and_category[0])
        return keywords
