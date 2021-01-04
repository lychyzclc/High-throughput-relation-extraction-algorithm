class LoadTypelist:
    def __init__(self, filepath):
        self.filepath = filepath
        self.type_dic = {}

    def Load(self):
        with open(self.filepath) as f:
            lines = f.readlines()
            for line in lines:
                line_list = line.split('|')
                self.type_dic[line_list[3].strip()] = line_list[2].lower()
        return self.type_dic
