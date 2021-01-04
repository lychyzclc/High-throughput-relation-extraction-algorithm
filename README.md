# High-throughput-relation-extraction-algorithm

Hi-RES: High-throughput relation extraction algorithm development associating knowledge articles and electronic health records

This is a repository of ETL pipeline in project [Hi-RES](https://arxiv.org/ftp/arxiv/papers/2009/2009.03506.pdf).

## Requirements

- pandas==1.1.3
- tqdm==4.45.0
- torch==1.7.0+cu110
- numpy==1.18.3
- PyMySQL==0.9.3
- spacy==2.2.2
- A Spacy model is employed to split text. Download it with `pipreqs . --encoding=utf8 --force`

## Processing pipeline-for Positive Samples

### 1. split_text.py  
DEPENDENCY: spacy  
- INPUT: structured text  
- OUTPUT: split into sentences  
- NOTE:  
1) '-m' is used to indicate multiprocess mode, if used, 8 files named from 'sent_all_0.txt' to 'sent_all_7.txt' will be generated.  
2) 'error.txt' is the record of articles that fail to be split due to structure problem or length problem(too long to be split by spacy)  

PARAMETERS:  
- input_file: All_text_new.txt  
- text_length: num of rows of All_text_new.txt  
- output_file: sent_all_%d.txt  
- error_file: error.txt  
- -m: multiprocess True  

### 2. NER  

### 3. Trie_entitypair.py
- generate trie_positive_ep.pkl from database
- PARAMETERS: save_path, load_path, db_name, table_name
- not written with argparse, modification needed

### 4. DrawSentence_main.py  

- INPUT: sentences and NER result  
- OUTPUT: sentences that contain target entitypairs  
- PARAMETERS:  
- For generating positive samples  
  db_name: relations  
  table_name: disease_bodypart  
  save_path: trie_positive_ep.pkl  
  NER_file: NERresult_%d.txt  
  sent_file: sent_all_%d.txt  
  output_file: Entitypair_%d.txt  
  num: 9 (num of files to process)  
- For generating negative samples(class 3)  
  db_name:umls0  
  table_name:sorted_pairs  
  save_path:trie_negative_ep.pkl  
  NER_file:NERresult_%d.txt  
  sent_file:sent_all_neg_%d.txt  
  output_file:Entitypair_neg_%d.txt  
  num: 9 (num of files to process)  
```
python Drawsentence_main.py relations disease_bodypart trie_positive_ep.pkl NERresult_ sent_all_ Entitypair_ 9

cat Entitypair_0.txt Entitypair_1.txt Entitypair_2.txt Entitypair_3.txt Entitypair_4.txt Entitypair_5.txt Entitypair_6.txt Entitypair_7.txt Entitypair_8.txt > Entitypair_all.txt  
(The same with Entitypair_neg_all.txt)  
```

### 5. general_clean_1.py
- INPUT: the result of DrawSentence  
- OUTPUT: the sentences after mask and position calculation, discard too short sentences (output in exception file).  
- PARAMETERS:  
  type_path: A0002SemGroups.txt  
  input_file: Entitypair_all.txt  
  output_file: general_clean_all.txt  
  exception_path: length_exception.txt  
- For generating negative samples(class 3)  
  type_path:A0002SemGroups.txt  
  input_file: Entitypair_neg_all.txt  
  output_file: general_clean_neg_all.txt  
  exception_path:length_exception_neg.txt  
```
python general_clean_1.py A0002SemGroup.txt Entitypair_all.txt general_clean_all.txt length_exception_neg.txt
```
  
### 6. customized further cleaning for different relations
- For DISO-DISO relations
  - diso_adjust_order.py  
adjust order of entities so that entity1 must appear before entity2
INPUT: general_clean_diso_diso_1.txt  
OUTPUT: general_clean_diso_diso_2.  
  - further_clean.py  
delete some too general concepts, specific text patterns
INPUT: general_clean_diso_diso_2.txt  
OUTPUT: further_clean_diso_diso.txt  
  - split_diso.py  
split the files into 3 relations   
INPUT: further_clean_diso_diso.txt  
OUTPUT: further_clean_ddx.txt  
      further_clean_mc.txt  
      further_clean_mbc.txt  


### 7. group_embedding.py  
- INPUT: result of further clean  
- OUTPUT: samples grouped by entitypairs and with cui embeddings  
- PARAMETERS:  
  input_file: further_clean_2.txt  
  output_file: positive_sample_2.txt  
  embed_path: embed_dic.pkl  
  label: 1
  sample_type(indicate different types of negative samples, 0 for positive samples): 0
- For generating negative samples(class 3)  
  input_file: further_clean_neg%d_2.txt  
  output_file: negative_sample%d_2.txt  
  embed_path: embed_dic.pkl  
  label: 0
  sample_type: 3
```
python group_embedding.py further_clean_2.txt positive_sample_2.txt embed_dic.pkl 1 0
```
- For DISO-DISO relations
```
python group_embedding.py ../data/further_clean_ddx.txt ../data/positive_sample_ddx.txt ../data/embed_dic.pkl 1 0
python group_embedding.py ../data/further_clean_mc.txt ../data/positive_sample_mc.txt ../data/embed_dic.pkl 2 0
python group_embedding.py ../data/further_clean_mbc.txt ../data/positive_sample_mbc.txt ../data/embed_dic.pkl 3 0


## Contact

If you have any comments or suggestions about this repository, please feel free to contact [Yucong Lin]() or [Keming Lu](lkm16@tsinghua.org.cn)

To request any necessary data to run this ETL pipeline, please contact [Sheng Yu syu@tsinghua.edu.cn](syu@tsinghua.edu.cn)
