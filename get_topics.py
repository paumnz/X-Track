import re
import numpy as np
import pandas as pd
import gensim
import spacy
from nltk.corpus import stopwords
from sqlalchemy import create_engine
from collections import Counter
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from pprint import pprint
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from PIL import Image
import matplotlib.colors as mcolors

class Topics:
    def __init__(self, db_connection, pymongo_conn, campaigns, hashtags, k, writer):
        self._db_connection = db_connection
        self._pymongo_conn = pymongo_conn
        self._campaigns = campaigns
        self._hashtags = hashtags
        self._k = k
        self._writer = writer

    def _get_tweets(self):
        """
        Fetches tweets from the database based on specified campaigns and hashtags.
        """
        if self._hashtags:
            query = """
            SELECT text, like_count, retweet_count 
            FROM tweet, tweet_metrics, hashtagt_tweet, hashtag
            WHERE (lang='en' OR lang='fr' OR lang='es')
            AND tweet_metrics.tweet_id=tweet.id
            AND tweet.campaign IN %s
            AND hashtag.hashtag IN %s
            AND hashtagt_tweet.tweet_id=tweet.id 
            AND hashtagt_tweet.hashtag_id=hashtag.id;
            """
            params = (tuple(self._campaigns), tuple(self._hashtags))
        else:
            query = """
            SELECT text, like_count, retweet_count 
            FROM tweet, tweet_metrics
            WHERE (lang='en' OR lang='fr' OR lang='es')
            AND tweet_metrics.tweet_id=tweet.id
            AND tweet.campaign IN %s;
            """
            params = (tuple(self._campaigns),)

        tweets = pd.read_sql(query, con=self._db_connection, params=params)
        return tweets

    def _sent_to_words(self, sentences):
        """
        Preprocesses sentences for analysis by removing special characters and stopwords.
        """
        for sent in sentences:
            sent = re.sub(r'\S*@\S*\s?', '', sent)
            sent = re.sub(r'\s+', ' ', sent)
            sent = re.sub(r"\'", "", sent)
            sent = re.sub(r'http\S+', '', sent)
            sent = re.sub(r'www\S+', '', sent)
            sent = re.sub(r'[^\w\s]', '', sent)
            sent = gensim.utils.simple_preprocess(str(sent), deacc=True)
            yield sent

    def _process_words(self, texts, stop_words, bigram_mod, trigram_mod, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        """
        Processes texts to remove stopwords, form bigrams and trigrams, and lemmatize the texts.
        """
        texts = [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]
        texts = [bigram_mod[doc] for doc in texts]
        texts = [trigram_mod[bigram_mod[doc]] for doc in texts]
        texts_out = []
        nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
        for sent in texts:
            doc = nlp(" ".join(sent))
            texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
        texts_out = [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts_out]
        return texts_out

    def _format_topics_sentences(self, ldamodel, corpus, texts):
        """
        Formats the topics in sentences for analysis.
        """
        sent_topics_df = pd.DataFrame()

        for i, row_list in enumerate(ldamodel[corpus]):
            row = row_list[0] if ldamodel.per_word_topics else row_list
            row = sorted(row, key=lambda x: (x[1]), reverse=True)
            for j, (topic_num, prop_topic) in enumerate(row):
                if j == 0:
                    wp = ldamodel.show_topic(topic_num)
                    topic_keywords = ", ".join([word for word, prop in wp])
                    sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic, 4), topic_keywords]), ignore_index=True)
                else:
                    break
        sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']
        contents = pd.Series(texts)
        sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
        return sent_topics_df

    def _gen_clouds(self, stop_words, lda_model):
        """
        Generates word clouds for each topic.
        """
        cols = [color for name, color in mcolors.TABLEAU_COLORS.items()]
        cloud = WordCloud(stopwords=stop_words, background_color='white', width=2500, height=1800, max_words=10, colormap='tab10', prefer_horizontal=1.0)

        topics = lda_model.show_topics(formatted=False)
        fig, axes = plt.subplots(2, 2, figsize=(10, 10), sharex=True, sharey=True)

        for i, ax in enumerate(axes.flatten()):
            fig.add_subplot(ax)
            topic_words = dict(topics[i][1])
            cloud.generate_from_frequencies(topic_words, max_font_size=300)
            plt.gca().imshow(cloud)
            plt.gca().set_title('Topic ' + str(i), fontdict=dict(size=16))
            plt.gca().axis('off')

        plt.subplots_adjust(wspace=0, hspace=0)
        plt.axis('off')
        plt.margins(x=0, y=0)
        plt.tight_layout()
        fig.savefig('word_clouds_topic.png', dpi=fig.dpi)

    def _map_impact(self, x):
        """
        Calculates the impact of a tweet based on retweets and likes.
        """
        return 2 * x["retweet_count"] + x["like_count"] + 2

    def _map_topic_names(self, x, keywords):
        """
        Maps topic numbers to their keywords.
        """
        topic_num = x["topic"]
        topic_tag = keywords.loc[keywords['Topic_Num'] == topic_num]["Keywords"].to_list()
        topic_tag = ",".join(topic_tag[:3])
        return f"{topic_num}: {topic_tag}"

    def _gen_map(self, tweets, lda_model, corpus, keywords):
        """
        Generates a 2D t-SNE map of the topics.
        """
        topic_weights = []
        for i, row_list in enumerate(lda_model[corpus]):
            topic_weights.append([w for i, w in row_list[0]])

        arr = pd.DataFrame(topic_weights).fillna(0).values
        tsne_model = TSNE(n_components=2, verbose=1, random_state=0, angle=.99, init='pca')
        tsne_lda = tsne_model.fit_transform(arr)

        topic_num = np.argmax(arr, axis=1)

        tweets["topic"] = topic_num
        tweets["x"] = tsne_lda[:, 0]
        tweets["y"] = tsne_lda[:, 1]
        tweets["impact"] = tweets.apply(self._map_impact, axis=1)
        tweets["topic_tags"] = tweets.apply(lambda x: self._map_topic_names(x, keywords), axis=1)

        fig = px.scatter(x=tweets["x"], y=tweets["y"], color=tweets["topic_tags"], size=tweets["impact"], labels={"color": "Conversation"})
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.write_image("conversation_map.png")

        tweet_groups = tweets.groupby('topic')["impact"].count().sort_values(ascending=False)[:20].to_frame().reset_index()
        fig_bars = px.bar(tweet_groups, x='topic', y='impact', labels={"topic": "Topic", "impact": "Number of Tweets"})
        fig_bars.write_image("topics_impact.png")

    def gen_topics(self):
        """
        Generates topics from tweets and saves results.
        """
        tweets = self._get_tweets()
        print(len(tweets))
        data = tweets.text.values.tolist()
        data_words = list(self._sent_to_words(data))

        stop_words = stopwords.words('english')
        stop_words.extend(stopwords.words('spanish'))
        stop_words.extend(stopwords.words('french'))
        stop_words.extend(stopwords.words('german'))
        stop_words.extend(['from', 'subject', 're', 'edu', 'use', 'not', 'would', 'say', 'could', '_', 'be', 'know', 'good', 'go', 'get', 'do', 'am', 'pm', 'wtf', 'lol', 'brb', 'lmao', 'rofl', 'idk'])

        bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100)
        trigram = gensim.models.Phrases(bigram[data_words], threshold=100)
        bigram_mod = gensim.models.phrases.Phraser(bigram)
        trigram_mod = gensim.models.phrases.Phraser(trigram)

        data_ready = self._process_words(data_words, stop_words, bigram_mod, trigram_mod)

        id2word = corpora.Dictionary(data_ready)
        corpus = [id2word.doc2bow(text) for text in data_ready]

        print("[+] Building LDA model")
        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=id2word, num_topics=4, random_state=100, update_every=1, chunksize=10, passes=10, alpha='symmetric', iterations=100, per_word_topics=True)

        df_topic_sents_keywords = self._format_topics_sentences(ldamodel=lda_model, corpus=corpus, texts=data_ready)
        df_dominant_topic = df_topic_sents_keywords.reset_index()
        df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']
        print("[+] Writing topic model to excel")
        df_dominant_topic.head(50).to_excel(self._writer, sheet_name='tweet_dominant_topic', index=False, header=True)

        sent_topics_sorteddf_mallet = pd.DataFrame()
        sent_topics_outdf_grpd = df_topic_sents_keywords.groupby('Dominant_Topic')

        for i, grp in sent_topics_outdf_grpd:
            sent_topics_sorteddf_mallet = pd.concat([sent_topics_sorteddf_mallet, grp.sort_values(['Perc_Contribution'], ascending=False).head(1)], axis=0)

        sent_topics_sorteddf_mallet.reset_index(drop=True, inplace=True)
        sent_topics_sorteddf_mallet.columns = ['Topic_Num', "Topic_Perc_Contrib", "Keywords", "Representative Text"]
        print("[+] Writing topic summary to excel")
        sent_topics_sorteddf_mallet.to_excel(self._writer, sheet_name='topic_list', index=False, header=True)

        print("[+] Generating topic word clouds")
        self._gen_clouds(stop_words, lda_model)
        print("[+] Generating conversation map")
        self._gen_map(tweets, lda_model, corpus, sent_topics_sorteddf_mallet)

