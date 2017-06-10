from jlam.py_sql import PySql
import jlam.conn_constants as cnst
import timecard_sql as tc_sql
import jlam.nltk_util as nl_ut
import nltk
import jlam.dict_util as du

COLUMNS = ['mon_note','tue_note','wed_note','thu_note','fri_note','timecard_note']

def get_tc_notes_df(startDate,endDate):
    sfdc=PySql(cnst.SVR_BIODS,cnst.DB_SFDC_DATA)
    sql = tc_sql.get_tc_notes(startDate,endDate)
    return sfdc.fetchDF(sql)

def tag_all_words(df):
    all_words=get_all_words(df)
    #return nltk.pos_tag(all_words)
    tagger = nl_ut.get_brill_tagger()
    return tagger.tag(all_words)

def get_all_words(df):
    tokenizer=nl_ut.get_regex_tokenizer()
    sw = nl_ut.get_stopwords(['none','concur',',','.','&','-','(',')','/',';',':','#','+'])
    all_words = []
    for idx, row in df.iterrows():
        for col in COLUMNS:
            #words = nltk.word_tokenize(row[col])
            words = tokenizer.tokenize(row[col])
            for x in words:
                if x not in sw:
                        all_words.append(x)
    return all_words

def get_sat_notes_count(df):
    '''
        create a dictionaries of sat, project name, and note counts within each
    '''
    sat_notes = {}
    for idx, row in df.iterrows():
        cur_sat = row['sat']
        cur_pj = row['pj_name']
        sat_dict = du.get_dict_from_dict(sat_notes,cur_sat)
        pj_dict = du.get_dict_from_dict(sat_dict,cur_pj)
        for col in COLUMNS:
            note = row[col]
            du.update_dict(pj_dict,note)
    return sat_notes