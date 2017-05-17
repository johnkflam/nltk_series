from nltk.corpus import stopwords
import nltk
from jlam.py_sql import PySql
import jlam.conn_constants as cnst
import codecs

concur_stopwords = ['profile-profile','profile-user','profile','profiles','invoice','invoices','travel','expense','expenses','error','user'
        ,'-',"'","/","concur",'profile-user','profile-','#',"(",")"]

TOPIC_TRAVEL = 'Travel'
TOPIC_EXPENSE = 'Expense'
TOPIC_INVOICE = 'Invoice'

# word type
WORD_TYPE_NOUN = 'Noun'
WWORD_TYPE_VERB = 'Verb'
WWORD_TYPE_ALL = 'All'
        
        
def get_classifier_naive_bay(trainSet):
    ''' train set should have a feature set and a target,
        example : ({'first_letter': 'l', 'last_letter': 's', 'length': 15},'male')
    '''
    return nltk.NaiveBayClassifier(trainSet)

def get_classifier_accuracy(classifier,testSet):
    ''' return accuracy of a classifer '''
    return nltk.classify.accuracy(classifier,testSet)

def get_classifier_most_informative_features(classifier,top):
    return classifier.most_informative_features(top)

def get_stopwords():
    return set(stopwords.words("english"))
    
    
def add_custom_stopwords(stopwords):
    sw = get_stopwords()
    for x in stopwords:
        sw.add(x)
    return sw

def part_of_speech_tag(msg):
    return nltk.pos_tagged(msg)


def get_cases_df():
    sfdc=PySql(cnst.SVR_BIODS,cnst.DB_SFDC_DATA)
    sql='''
        select 
        topic__c,case_type__c,subject
        from dbo.[case] c
        left join dbo.RecordType r on (c.recordTypeId=r.id)
        where c.createddate >= '2017-01-01'
        and team__c in ('Call Center 1','Call Center 2','Call Center 3','Call Center Manila','Call Center Prague','Call Center US','Call Center UK'
                ,'Expense Support - Professional','Expense Solutions'
                ,'Expense Support - Standard'
                ,'Travel Support','Travel Solutions','Travel Support 3PTY'
                ,'Invoice Support'
                ,'T&E Cross Product TRIM'
                ,'Expense E100 Support'
                        -- R&D cases
                        ,'Expense Support R&D'
                        ,'Travel Support R&D'
                        ,'Cross Product Support R&D')
                   and topic__c in ('Travel','Expense','Invoice')            
        '''
    return sfdc.fetchDF(sql)

def tokenize(df,case_type):
    sw = add_custom_stopwords(concur_stopwords)
    
    # make sure we filter words from case type
    ary = case_type.lower().split(" ")
    sw = add_custom_stopwords(ary)
    all_words=[]
    for idx, row in df.iterrows():
        words = nltk.word_tokenize(row['subject'].lower())
        for x in words:
            if x not in sw:
                all_words.append(x)
    return all_words


def get_topic_most_common_words(topic,df,word_type,max_rank):
    lst_of_common_words=[]
    
     # get df by topic 
    if topic==TOPIC_TRAVEL:
        df_topic = df[df.topic__c==TOPIC_TRAVEL]
    elif topic==TOPIC_EXPENSE:
        df_topic = df[df.topic__c==TOPIC_EXPENSE]
    else:
        df_topic = df[df.topic__c==TOPIC_INVOICE]
        
    lst_case_type=df_topic.case_type__c.unique()
        
    for ct in lst_case_type:
        df_case_type=df_topic[df['case_type__c']==ct]
        words=get_words_by_type(df_case_type,word_type,ct)
        
        # get most frequent distribution
        freq_words = nltk.FreqDist(words)
        most_common = freq_words.most_common(max_rank)
        
        dic={'topic':topic,'case_type':ct,'most_common':most_common}
        lst_of_common_words.append(dic)
        
    return lst_of_common_words
        
def get_words_by_type(df,word_type,case_type):
    tokenized = tokenize(df,case_type)
    tagged = nltk.pos_tag(tokenized)
    
    if word_type==WORD_TYPE_NOUN:
        words=[x[0] for x in tagged if x[1]=='NN' or x[1]=='NNS']
    elif word_type==WORD_TYPE_VERB:
        words=[x[0] for x in tagged if x[1]=='VB' or x[1]=='VBD']
    else:
        words=tagged
        
    return words
    
def write_to_file(topic,common_words):
    f=codecs.open('{0}_case_type_most_common_word.csv'.format(topic),'w','utf-8')
    f.write('''topic\tcase type\tword\tfrequency\n''')
    topic='invoice'
    for r in common_words:
        case_type=r['case_type']
        most_common = r['most_common']
        for w in most_common:
            f.write(u"{0}\t{1}\t{2}\t{3}\n".format(topic,case_type,w[0],w[1]))
    f.close()    
         
def main():
    '''
        product : Travel, Expense, or Invoice
        max_freq: maximum # of common words
        word_type: all, noun, or verb
    '''
    # get df for topic,case_type, and 
    df = get_cases_df()
   
    topics=[TOPIC_EXPENSE,TOPIC_TRAVEL,TOPIC_INVOICE]
    
    for topic in topics:
        common_words=get_topic_most_common_words(topic,df,WORD_TYPE_NOUN,15)
        write_to_file(topic,common_words)
        
    print 'done'
    