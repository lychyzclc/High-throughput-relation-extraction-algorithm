#!/bin/bash

input_file=output_disolab/general_cleaning.txt # input general cleaning file
output_file=output_disolab/positive.txt # output entity pair file
log_file=output_disolab/log

data_dir=data # data directory
embed_file=embed_dic.pkl # ehr embeddings
relation_mapping_file=relation2idx_diso_lab.pkl # a pickle file to transform relation terms to indice

echo "[step5] group embedding begin"
python -u src/step5_group_embedding.py\
       	--input_file ${input_file}\
       	--output_file ${output_file}\
       	--log_file ${log_file}\
       	--embed_file ${data_dir}/${embed_file}\
	--label ${data_dir}/${relation_mapping_file}
echo "[step5] group embedding finish"
