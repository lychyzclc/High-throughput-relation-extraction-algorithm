class Sentence:
	def __init__(self, line_list):
		self.article_id = line_list[0]
		self.sent_id = line_list[1]
		self.cui1 = line_list[2]
		self.type1 = line_list[3]
		self.cui2 = line_list[4]
		self.type2 = line_list[5]
		self.text = line_list[6]
		self.article_structure = line_list[7]
		self.pos1 = eval(line_list[8])
		self.pos2 = eval(line_list[9])
		self.text_length = len(self.text.split())
		self.is_title1 = int(line_list[11])
		self.is_title2 = int(line_list[12])

	def __str__(self):
		return str(self.article_id)+'|'+str(self.sent_id)+'|'+str(self.cui1) + '|'+ str(self.type1) + '|' + str(self.cui2) +'|' + str(self.type2)\
		+'|'+ str(self.text)+'|'+ str(self.article_structure)+'|'+str(self.pos1)+'|'+str(self.pos2)\
		+'|' +str(self.text_length)+'|'+str(self.is_title1)+'|'+str(self.is_title2)+ '\n'

class LoadSentences:
	def __init__(self, filepath):
		self.filepath = filepath

	def Process(self, line):
		line_list = line.strip().split('|')
		return Sentence(line_list)

	def Reader(self):
		f = open(self.filepath)
		line = f.readline()
		while line:
			yield self.Process(line)
			line = f.readline()
		f.close()
