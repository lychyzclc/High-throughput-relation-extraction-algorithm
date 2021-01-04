#!/bin/bash

task_name=${1}
input_file=${2}
output_dir=${3}
error_dir=${output_dir}/error
log_dir=${output_dir}/log

terms_file=terms.pkl # cui terms from term table
trie_file=trie.pkl # trie of cui terms
embed_file=embed_dic.pkl # ehr embedding
group_file=A0002SemGroups.txt # semantic group table from UMLS
relation_file=diso_lab_relation.txt # relation tripets
relation_trie_file=trie_diso_lab.pkl # trie for entity pairs in relation triplets
data_dir=data # data directory
num_proc=8 # process number

# calculate row num of input file
input_file_row_cnt=`wc -l ${input_file} | awk '{print $1}'`
echo "row count of input file ${input_file} is ${input_file_row_cnt}"


# create output dir
if [ ! -d ${output_dir} ];then
	echo "create output directory ${output_dir}"
	mkdir ${output_dir}
else
	echo "${output_dir} exists"
fi
if [ ! -d ${error_dir} ];then
	echo "create exception directory ${error_dir}"
	mkdir ${error_dir}
else
	echo "${error_dir} exists"
fi
if [ ! -d ${log_dir} ];then
	echo "create exception directory ${log_dir}"
	mkdir ${log_dir}
else
	echo "${log_dir} exists"
fi

# preprocessing of corpus and entity linking
echo "[step1] split text begin"
python -u src/step1_split_text.py \
	--input_file ${input_file} \
	--text_length ${input_file_row_cnt} \
	--output_file ${output_dir}/${task_name} \
	--error_file ${error_dir}/step1.error \
	--log_file ${log_dir}/step1.log \
	--proc ${num_proc}
echo "[step1] split text finish"

echo "[step2] entity linking begin"
python -u src/step2_entity_linking.py \
	--input_file ${output_dir}/${task_name}\
	--output_file ${output_dir}/${task_name}_NER_\
	--data_dir ${data_dir}\
	--terms_file ${terms_file}\
	--trie_file ${trie_file}\
	--log_file ${log_dir}/step2.log\
	--proc ${num_proc}
echo "[step2] entity linking finish"

# distant supervision
echo "[step3] draw sentence begin"
python -u src/step3_draw_sentence.py\
       	--relation_path ${data_dir}/${relation_file}\
       	--save_path ${data_dir}/${relation_trie_file}\
       	--NER_file ${output_dir}/${task_name}_NER_\
       	--sent_file ${output_dir}/${task_name}\
       	--output_file ${output_dir}/${task_name}_entitypair_\
	--log_file ${log_dir}/step3.log\
       	--proc ${num_proc} 
cat ${output_dir}/${task_name}_entitypair_* > ${output_dir}/${task_name}_entitypair_all.txt
echo "[step3] draw sentence finish"

echo "[step4] general cleaning begin"
python -u src/step4_general_clean.py\
       	--type_path ${data_dir}/${group_file}\
       	--input_file ${output_dir}/${task_name}_entitypair_all.txt\
	--output_file ${output_dir}/${task_name}_general_cleaning.txt\
       	--error_file ${error_dir}/step4.error\
	--log_file ${log_dir}/step4.log
echo "[step4] general cleaning finish"
