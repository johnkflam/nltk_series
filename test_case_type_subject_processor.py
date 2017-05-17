import unittest
import nltk_util as nu

class TestCaseTypeSubjectProcessor(unittest.TestCase):
    def setUp(self):
        self.df = nu.get_cases_df()
     
    @unittest.skip('skip for now')
    def test_get_cases_df(self):
        df = nu.get_cases_df()
        self.assertTrue(len(df>50),"cases df is null or zero length")
    
   
    def test_get_topic_most_common_words(self):
        lst_of_common_words=nu.get_topic_most_common_words(nu.TOPIC_INVOICE, self.df, nu.WORD_TYPE_NOUN,50)
        self.assertTrue(lst_of_common_words<>None,'list of freqent words is null')
        e= lst_of_common_words[0]
        self.assertTrue(e['topic']==nu.TOPIC_INVOICE and e['case_type']<>None and e['most_common']<>None,'invalid common words dict')
        #print lst_of_common_words
        
    
if __name__ == '__main__':
    unittest.main()