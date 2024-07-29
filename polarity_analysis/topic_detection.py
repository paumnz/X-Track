
import pandas as pd
import numpy as np
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from nltk.corpus import stopwords
import string
import matplotlib.pyplot as plt
import gensim
from gensim import corpora

import numpy as np
from gensim.models import CoherenceModel, LdaModel, LsiModel, HdpModel
#from gensim.models.wrappers import LdaMallet
from gensim.corpora import Dictionary
import spacy

import seaborn as sns
import matplotlib.pyplot as plt

import logging

logging.basicConfig(
    format = '%(asctime)-5s %(name)-15s %(levelname)-8s %(message)s', 
    level  = logging.ERROR, 
)



class topic_detection:


    def __init__(self, engine, black_list=[])-> None:
        nltk.download('stopwords')
        nltk.download('punkt')

        self._engine=engine
        self._black_list=black_list

        self._stop = set(stopwords.words('english'))
        self._additional_stopwords=set(self._black_list)
        self._stopwords = self._stop.union(self._additional_stopwords)

        self._nlp = spacy.load('en_core_web_md')

    def _hdp(self, campaign_topic):
        pass

    def _lsi(self, campaign_topic):
        pass

    def _lda(self, text_df,  max_topics=20, field="text_clean"):


        dirichlet_dict = Dictionary(text_df[field].to_list())
        bow_corpus = [dirichlet_dict.doc2bow(text) for text in text_df[field].to_list()]

        num_topics = list(range(max_topics+1)[1:])
        num_keywords = max_topics

        LDA_models = {}
        LDA_topics = {}
        i=0

        for i in num_topics:
            LDA_models[i] = LdaModel(corpus=bow_corpus,
                                    id2word=dirichlet_dict,
                                    num_topics=i,
                                    update_every=1,
                                    chunksize=len(bow_corpus),
                                    passes=20,
                                    alpha='auto',
                                    random_state=42)

            shown_topics = LDA_models[i].show_topics(num_topics=i, 
                                                    num_words=num_keywords,
                                                    formatted=False)
            LDA_topics[i] = [[word[0] for word in topic[1]] for topic in shown_topics]

        print(LDA_models)
        LDA_stability = {}
        i=0
        for i in range(0, len(num_topics)-1):
            jaccard_sims = []
            for t1, topic1 in enumerate(LDA_topics[num_topics[i]]): # pylint: disable=unused-variable
                sims = []
                for t2, topic2 in enumerate(LDA_topics[num_topics[i+1]]): # pylint: disable=unused-variable
                    sims.append(self._jaccard_similarity(topic1, topic2))    
                
                jaccard_sims.append(sims)    
            
            LDA_stability[num_topics[i]] = jaccard_sims
        i=0           
        mean_stabilities = [np.array(LDA_stability[i]).mean() for i in num_topics[:-1]]

        i=0

        coherences = [CoherenceModel(model=LDA_models[i], texts=text_df[field].to_list(), dictionary=dirichlet_dict, coherence='c_v').get_coherence()\
              for i in num_topics[:-1]]

        i=0
        coh_sta_diffs = [coherences[i] - mean_stabilities[i] for i in range(num_keywords)[:-1]] # limit topic numbers to the number of keywords
        coh_sta_max = max(coh_sta_diffs)
        coh_sta_max_idxs = [i for i, j in enumerate(coh_sta_diffs) if j == coh_sta_max]
        ideal_topic_num_index = coh_sta_max_idxs[0] # choose less topics in case there's more than one max
        ideal_topic_num = num_topics[ideal_topic_num_index]
        print(ideal_topic_num)
        return LDA_models[ideal_topic_num], bow_corpus

    def _find_topic(self, row, alpha=0.85):

        if (row.loc[row>alpha]).any():
            return row.loc[row>alpha].index[0]
        else:
            return None
    
    def _find_propensity(self, row, alpha=0.85):
        if (row.loc[row>alpha]).any():
            return row.loc[row>alpha].values[0]
        else:
            return None

    def _cleaner(self, word):

            word = re.sub(r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*', '', word, flags=re.MULTILINE)
            word = re.sub(r'(?::|;|=)(?:-)?(?:\)|\(|D|P)', "", word)
            word = re.sub(r'ee.uu', 'eeuu', word)
            word = re.sub(r'\#\.', '', word)
            word = re.sub(r'\n', '', word)
            word = re.sub(r',', '', word)
            word = re.sub(r'_', '', word)
            word = re.sub(r'\*', '', word)
            word = re.sub(r'\-', ' ', word)
            word = re.sub(r'\.{3}', ' ', word)
            word = re.sub(r'á', 'a', word)
            word = re.sub(r'é', 'e', word)
            word = re.sub(r'í', 'i', word)
            word = re.sub(r'ó', 'o', word)
            word = re.sub(r'ú', 'u', word)  
            word = re.sub('[^a-zA-Z]', ' ', word)
            list_word_clean = []
            for w1 in word.split(" "):
                if  w1.lower() not in self._stopwords:
                    list_word_clean.append(w1.lower())

            bigram_list = self._bigram[list_word_clean]
            out_text = self._lemmatization(" ".join(bigram_list))

            return out_text

    def _lemmatization(self, texts, allowed_postags=['NOUN']):

        # corpus for news in spanish, check language

        texts_out = [ token.text for token in self._nlp(texts) if token.pos_ in 
                    allowed_postags and token.text not in self._black_list and len(token.text)>2]
        return texts_out

    def _jaccard_similarity(self, topic_1, topic_2):
        """
        Derives the Jaccard similarity of two topics

        Jaccard similarity:
        - A statistic used for comparing the similarity and diversity of sample sets
        - J(A,B) = (A ∩ B)/(A ∪ B)
        - Goal is low Jaccard scores for coverage of the diverse elements
        """
        intersection = set(topic_1).intersection(set(topic_2))
        union = set(topic_1).union(set(topic_2))
                        
        return float(len(intersection))/float(len(union))

    def _gen_campaign_df(self, campaign):
        q='''
        select tweet.text as text, GROUP_CONCAT(hashtag.hashtag SEPARATOR ", ") as hashtag_list from tweet, hashtagt_tweet, hashtag 
        where hashtagt_tweet.tweet_id=tweet.id and hashtagt_tweet.hashtag_id=hashtag.id and tweet.campaign IN  ("%s") group by text''' %(campaign)
        
        text_df = pd.read_sql(q, con=self._engine)

        return text_df

    
    def _detect_topcis(self, text_df, campaign=None, method="lda", max_topics=20, field="text_clean") -> list:

        if method == "lda":
            topic_model, corpus = self._lda(text_df, max_topics, field)
            return topic_model, corpus

        
    def _gen_topic_df(self, corpus, text_df, topic_model):
         # extract all document-topic distritbutions to dictionnary
        document_key = list(text_df.index) ##get index of transcripts for topic in each
        document_topic = {}
        for doc_id in range(len(corpus)):
            docbok = corpus[doc_id]
            doc_topics = topic_model.get_document_topics(docbok, 0)
            tmp = []
            for topic_id, topic_prob in doc_topics:
                tmp.append(topic_prob)
            document_topic[document_key[doc_id]] = tmp
        # convert dictionnary of document-topic distritbutions to dataframe
        df = pd.DataFrame.from_dict(document_topic, orient='index')
        topic_column_names = ['topic_' + str(i) for i in range(0, topic_model.num_topics)]
        df.columns = topic_column_names
        df['text'] = (text_df['text'])

        return df

    def gen_day_tags(self, campaign, date, max_topics=20):

        q = '''

        select hashtag.hashtag as name, count(hashtag.id) as times from hashtag, tweet, hashtagt_tweet where hashtagt_tweet.tweet_id=tweet.id 
        and hashtagt_tweet.hashtag_id=hashtag.id and tweet.campaign IN("%s") 
        and DATE_FORMAT(tweet.created_at,"%%%%Y-%%%%m-%%%%d")="%s" 
        group by name order by times desc limit %s
        ''' % (campaign, date, max_topics)

        texts = pd.read_sql(q, con=self._engine)

        return texts["name"].to_list()

    def gen_tags_all(self, campaign, max_topics=20):

        q = '''

        select hashtag.hashtag as name, count(hashtag.id) as times from hashtag, tweet, hashtagt_tweet where hashtagt_tweet.tweet_id=tweet.id 
        and hashtagt_tweet.hashtag_id=hashtag.id and tweet.campaign IN ("%s")
        group by name order by times desc limit %s
        ''' % (campaign,  max_topics)

        texts = pd.read_sql(q, con=self._engine)

        return texts["name"].to_list()


    def get_topic_tags(self, campaign, method="lda", max_topics=20, field="text_clean"):

        text_df = self._gen_campaign_df(campaign=campaign)
        logging.info('Initial text dataframe generated')

        self._bigram = gensim.models.Phrases(text_df.text.to_list())
        logging.info('text bigram generated')

        text_df["text_clean"] = text_df.apply(lambda x: self._cleaner(x["text"]), axis=1)
        text_df["hashtag_list"] = text_df.apply(lambda x: x["hashtag_list"].split(', '), axis=1)
        text_df["all_tags"] = texts.apply(lambda x: x["hashtag_list"]+x["text_clean"], axis=1)
        logging.info('text cleeaned')



        topic_model, corpus = self._detect_topcis(text_df, campaign, method, max_topics, field)

        logging.info('topic model generated')
        
        topic_df = self._gen_topic_df(corpus, text_df, topic_model)
        topic_df['topic'] = topic_df.loc[:, topic_df.columns !='text'].apply(self._find_topic, axis = 1)
        topic_df["hashtag"]=text_df["hashtag_list"]
        topic_tags = []
        print(topic_model)
        for i in range(topic_model.num_topics):
            topic = "topic_"+str(i)
            logging.info('topic: '+str(topic))
            tl = (topic_df[topic_df["topic"]==topic]["hashtag"].explode().unique())
            topic_tags.append(tl)

        logging.info("topic tags generated")
        print(topic_tags)
        return topic_tags






 





        

        