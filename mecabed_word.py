import pdb


class MecabedWord:
    def __init__(self, word_info):
        tips = word_info.split(',')
        name_and_type = tips[0].split('\t')
        if len(name_and_type) == 1:
            pdb.set_trace()
        name = name_and_type[0]
        type = name_and_type[1]
        self.name = name
        self.type = type
        self.subtype = tips[1]
