class ResultWords:
    def __init__(self, words):
        self.words = words

    def to_ranked_items(self):
        rank_dict = {}
        #items => ['対策', '鼻炎', '対策', 'うるおい', ...]
        for item in self.words:
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
