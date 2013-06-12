from analyzer import Analyzer

#日本語の形態素解析をする
#splitする
#動詞と名詞だけでキーワードクエリにする


class Converter:

    def split_janapese_query(self, query):
        analyzer = Analyzer()
        keywords = analyzer.pick_nouns_and_verbs(query)
        return keywords
