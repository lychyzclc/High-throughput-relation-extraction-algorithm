import re

import pandas as pd

from delete_big_words import DeleteBigWords
from delete_pattern import DeletePattern, DeleteSpecificType
from remove_up import RemoveUp

input_file = '../data/general_clean_disodiso_pred2_all.txt'
output_file1 = '../data/disodiso_pred_ups_remain.txt'
exception1 = '../data/disodiso_pred_ups_delete.txt'
output_file2 = '../data/disodiso_pred_bigword_remain.txt'
exception2 = '../data/disodiso_pred_bigword_delete.txt'
output_file3 = '../data/disodiso_pred_type_remain.txt'
exception3 = '../data/disodiso_pred_type_delete.txt'
output_file4 = '../data/further_clean_disodiso_pred_all.txt'
exception4 = '../data/disodiso_pred_pattern_delete.txt'

nearpardic_file = '../data/nearpardic.txt'
neardic_file = '../data/neardic.txt'
nearrbdic_file = '../data/nearrbdic.txt'

todelete = pd.read_csv('../data/timesafter.csv')
bigword_todelete = list(todelete['cui'])

pattern_same = re.compile('t[0-9][0-9][0-9] \( t[0-9][0-9][0-9] \)')
type_todelete = ['t049', 't033', 't050', 't019']

if __name__ == '__main__':
	print('removing ups...')
	upremover = RemoveUp(input_file, output_file1, exception1)
	upremover.init(nearpardic_file, nearrbdic_file, neardic_file)
	cnt = upremover.process()
	print('done')
	print('%d ups removed'%cnt)

	print('removing bigwords...')
	bigword_remover = DeleteBigWords(output_file1, output_file2, exception2, bigword_todelete)
	cnt = bigword_remover.process()
	print('done')
	print('%d big words removed'%cnt)

	print('removing type...')
	type_remover = DeleteSpecificType(output_file2, output_file3, exception3, type_todelete)
	cnt = type_remover.process()
	print('done')
	print('%d types removed'%cnt)

	print('removing pattern...')
	pattern_remover = DeletePattern(output_file3, output_file4, exception4, pattern_same)
	cnt = pattern_remover.process()
	print('done')
	print('%d patterns removed'%cnt)
