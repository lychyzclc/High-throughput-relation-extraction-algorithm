import pandas as pd

if __name__ == "__main__":
    cleanterms_path ="../data/A0004cleanterms2.txt"
    all_relation_path = "../data/relation_all.txt"
    target_relations = ("procedure_diagnoses", "lab_diagnoses")
    target_relation_path = "../data/diso_lab_relation.txt"

    cleanterms = pd.read_table(cleanterms_path, sep="|")
    cui2sty_table = cleanterms[["cui","sty"]].values
    cui2sty = {}
    for cui, sty in cui2sty_table:
        if cui not in cui2sty:
            cui2sty[cui] = sty

    all_relation = pd.read_table(all_relation_path, sep="|")
    target_relation = []
    for each in target_relations:
        target_relation.append(all_relation.loc[all_relation["relation"] \
                == each,["CUI1", "relation", "CUI2"]])
    target_relation = pd.concat(target_relation)
    cui1, relation, cui2 = target_relation.T.values

    type1 = [cui2sty[c] for c in cui1]
    type2 = [cui2sty[c] for c in cui2]

    output_table = {
            "cui1": cui1, 
            "type1": type1,
            "rel": relation,
            "cui2": cui2,
            "type2":type2
            }
    output_table = pd.DataFrame(output_table)
    output_table.to_csv(target_relation_path, sep="|", index=0, header=0)
