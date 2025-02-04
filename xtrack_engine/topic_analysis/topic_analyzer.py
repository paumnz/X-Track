"""
Module to implement the topic analysis functionality of XTRACK's engine.
"""


import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Tuple

import gensim
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import spacy
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from nltk.corpus import stopwords
from sklearn.manifold import TSNE
from tqdm.auto import tqdm
from wordcloud import WordCloud, STOPWORDS

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.database_connection.db_connector import DBConnector
from xtrack_engine.errors.config_errors import IllegalAnalysisConfigError


class TopicAnalyzer(Analyzer):
    """
    Class to implement the topic analysis functionality of XTRACK's engine.
    """


    def __init__(
            self,
            campaigns: str | Tuple[str, ...],
            db_connector: DBConnector,
            log_level: int = logging.INFO,
            language : str | Tuple[str, ...] = 'es',
            spacy_model_name : str = 'en_core_web_sm'
        ) -> None:
        """
        Constructor method for the TopicAnalyzer class.

        Args:
            campaign (str): the campaign to be analyzed.
            db_connector (DBConnector): the database connector to be used for the analysis.
            log_level (int): the log level to be used for filtering logs in the runtime.
            language (str): the language/s to be used for topic analysis.
            spacy_model_name (str): the SpaCy model to be used.
        """
        super().__init__(campaigns, db_connector, log_level)

        self.languages : Tuple[str, ...] = language if type(language) == tuple else (language, )
        self.spacy_model_name = spacy_model_name

        self.stop_words = stopwords.words('english')
        self.stop_words.extend(stopwords.words('spanish'))
        self.stop_words.extend(stopwords.words('french'))
        self.stop_words.extend(stopwords.words('german'))
        self.stop_words.extend(['from', 'subject', 're', 'edu', 'use', 'not', 'would', 'say', 'could', '_', 'be', 'know', 'good', 'go', 'get', 'do', 'am', 'pm', 'wtf', 'lol', 'brb', 'lmao', 'rofl', 'idk', 'rt'])


    @property
    def pre_computed_tweet_df_query(self) -> str:
        """ Property to retrieve the pre-computed tweet dataframe of the TopicAnalyzer. """
        return """
            SELECT tweet_text, impact, topic, topic_x_coord, topic_y_coord, topic_tags
            FROM topic_assignment_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s AND
                spacy_model_name = %(spacy_model_name)s
        """


    @property
    def pre_computed_topics_df_query(self) -> str:
        """ Property to retrieve the pre-computed topics dataframe of the TopicAnalyzer. """
        return """
            SELECT word, probability, topic
            FROM lda_topics_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s AND
                spacy_model_name = %(spacy_model_name)s
        """


    def __retrieve_tweets(self, hashtags) -> pd.DataFrame:
        """
        Method to retrieve the tweets of the given campaigns and filtered by hashtags if provided.

        Args:
            hashtags: the hashtags with which to filter tweet retrieval.

        Returns:
            A Pandas DataFrame containing the tweets published on the current campaign and hashtags (if any).
        """
        self.logger.debug(f'Retrieving the tweets published on the campaign')

        if hashtags is None:
            query = """
                SELECT text AS tweet_text, like_count AS likes, retweet_count AS retweets
            FROM tweet
                INNER JOIN tweet_metrics tm ON tm.tweet_id = tweet.id
            WHERE
                tweet.lang IN %(languages)s AND
                tweet.campaign IN %(campaigns)s
            """
            params = {'campaigns': tuple(self.campaigns), 'languages' : self.languages}
        else:
            query = """
            SELECT text AS tweet_text, like_count AS likes, retweet_count AS retweets 
            FROM tweet
                INNER JOIN tweet_metrics tm ON tm.tweet_id = tweet.id
                INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
            WHERE
                tweet.lang IN %(languages)s AND
                tweet.campaign IN %(campaigns)s AND
                hashtag.hashtag IN %(hashtags)s;
            """
            params = {'campaigns': tuple(self.campaigns), 'languages' : self.languages, 'hashtags' : hashtags}

        tweet_df = self.db_connector.retrieve_table_from_sql(query, params)

        tweet_df['impact'] = 2 * tweet_df['retweets'] + tweet_df['likes'] + 2

        self.logger.debug(f'Retrieved the tweets published on the campaign')

        return tweet_df


    def __preprocess_tweets(self, tweet_texts : Tuple[str, ...]):
        """
        Private method to preprocess a tweet.
        """
        for tweet_text in tqdm(tweet_texts, desc = 'Pre-processing tweets to tokens'):
            tweet_text = re.sub(r'\S*@\S*\s?', '', tweet_text)
            tweet_text = re.sub(r'\s+', ' ', tweet_text)
            tweet_text = re.sub(r"\'", "", tweet_text)
            tweet_text = re.sub(r'http\S+', '', tweet_text)
            tweet_text = re.sub(r'www\S+', '', tweet_text)
            tweet_text = re.sub(r'[^\w\s]', '', tweet_text)
            tweet_text = gensim.utils.simple_preprocess(str(tweet_text), deacc=True)
            yield tweet_text


    def __load_spacy_preprocesser(self):
        """
        Private method to set up the SpaCy preprocesser.
        """
        try:
            # Try to load the model
            nlp = spacy.load(self.spacy_model_name)
            self.logger.debug(f"Model '{self.spacy_model_name}' loaded successfully.")
            return nlp
        except OSError:
            # If the model is not installed, catch the OSError and install the model
            self.logger.debug(f"Model '{self.spacy_model_name}' not found. Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "spacy", "download", self.spacy_model_name])
                nlp = spacy.load(self.spacy_model_name)
                self.logger.debug(f"Model '{self.spacy_model_name}' installed and loaded successfully.")
                return nlp
            except Exception as exc:
                raise IllegalAnalysisConfigError(f'Unable to download the given SpaCy model ({self.spacy_model_name}): exc')


    def __preprocess_tokenized_tweets_to_n_grams_and_lemmas(
            self,
            words_per_tweet : Tuple[Tuple[str], ...],
            allowed_postags : Tuple[str, ...] = ('NOUN', 'ADJ', 'VERB', 'ADV')
        ) -> Tuple[Tuple[str], ...]:
        """
        Private method to further preprocess the words of the given tweets using stopwords, bigrams and trigrams.

        Args:
            words_per_tweet (Tuple[str, ...]): a tuple of word tuples, where each word tuple is a preprocessed tweet.
            allowed_postags (Tuple[str, ...]): the postags to be kept when preprocessing the words.
        """
        self.logger.debug('Creating bi-gram and tri-gram models')

        # Step 1: Setting up the bigram and trigram models
        bigram = gensim.models.Phrases(words_per_tweet, min_count = 5, threshold = 100)
        trigram = gensim.models.Phrases(bigram[words_per_tweet], threshold = 100)
        bigram_mod = gensim.models.phrases.Phraser(bigram)
        trigram_mod = gensim.models.phrases.Phraser(trigram)

        self.logger.debug('Created bi-gram and tri-gram models')

        # Step 2: Applying N-Gram (2-grams and 3-grams) detection
        self.logger.debug('Detecting bi-grams and tri-grams')

        words_per_tweet = [[token for token in doc if token not in self.stop_words] for doc in words_per_tweet]
        words_per_tweet = [bigram_mod[doc] for doc in words_per_tweet]
        words_per_tweet = [trigram_mod[bigram_mod[doc]] for doc in words_per_tweet]

        self.logger.debug('Detected bi-grams and tri-grams')

        # Step 3: Applying lemmatization
        self.logger.debug('Lemmatizing tweets')

        lemmatized_tweets : List[Tuple[str, ...]] = []
        spacy_nlp = self.__load_spacy_preprocesser()

        for tokenized_tweet in tqdm(words_per_tweet, desc = 'Lemmatizing tweets'):
            doc = spacy_nlp(' '.join(tokenized_tweet))
            lemmatized_tweets.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])

        self.logger.debug('Lemmatized tweets')

        return lemmatized_tweets


    def __apply_topic_detection_model(self, tweet_tokens) -> pd.DataFrame:
        """
        Formats the topics in sentences for analysis.

        Args:
            tweet_tokens: the tuple of tuples of tokens, where each tuple of tokens represents a tokenized tweet.
        Returns:
            A Pandas DataFrame showing the dominant topic in each tweet.
        """
        sent_topics_list = []

        for i, row_list in enumerate(self.lda_model[self.corpus]):
            row = row_list[0] if self.lda_model.per_word_topics else row_list
            row = sorted(row, key=lambda x: (x[1]), reverse=True)
            for j, (topic_num, prop_topic) in enumerate(row):
                if j == 0:
                    wp = self.lda_model.show_topic(topic_num)
                    topic_keywords = ", ".join([word for word, prop in wp])
                    sent_topics_list.append([int(topic_num), round(prop_topic, 4), topic_keywords])
                else:
                    break

        sent_topics_df = pd.DataFrame(data = sent_topics_list, columns = ['Dominant_Topic', 'Topic_Perc_Contrib', 'Topic_Keywords'])
        contents = pd.Series(tweet_tokens)
        sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
        sent_topics_df = sent_topics_df.reset_index()
        sent_topics_df.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Topic_Keywords', 'Text']

        return sent_topics_df


    def __topic_detection(
            self,
            tweet_tokens : Tuple[Tuple[str, ...], ...],
            num_topics : int = 4
        ) -> Tuple[gensim.models.ldamodel.LdaModel, gensim.corpora.Dictionary, Any]:
        """
        Private method to carry out topic detection with LDA.

        Args:
            tweet_tokens: the tuple containing tuples of tokens representing the tokenized version of each tweet.
            num_topics: the number of topics to detect.

        Returns:
            A tuple (LdaModel, Dictionary, Corpus) containing the LDA model created, its dictionary and corpus.
        """
        self.logger.debug('Building LDA model')
        id2word = gensim.corpora.Dictionary(tweet_tokens)
        corpus = [id2word.doc2bow(text) for text in tweet_tokens]

        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=id2word, num_topics=num_topics, random_state=100, update_every=1, chunksize=10, passes=10, alpha='symmetric', iterations=100, per_word_topics=True)
        self.logger.debug('Built LDA model')

        return lda_model, id2word, corpus


    def __format_analysis_results(self, topics_df : pd.DataFrame) -> pd.DataFrame:
        """
        Method to format the analysis results.

        Args:
            topics_df (DataFrame): a Pandas DataFrame containing the most dominant topic in each tweet.

        Returns:
            A Pandas DataFrame containing the most representative tweet of each topic.
        """
        self.logger.debug('Formatting TopicAnalyzer results')

        final_topics_df = pd.DataFrame()
        sent_topics_outdf_grpd = topics_df.groupby('Dominant_Topic')

        for _, topic_group in sent_topics_outdf_grpd:
            final_topics_df = pd.concat([final_topics_df, topic_group.sort_values(['Topic_Perc_Contrib'], ascending=False).head(1)], axis=0)

        final_topics_df.reset_index(drop= True, inplace = True)
        final_topics_df = final_topics_df.drop(axis = 1, columns = ['Document_No'])
        final_topics_df.columns = ['Topic_Num', 'Topic_Perc_Contrib', 'Topic_Keywords', 'Representative_Text']

        self.logger.debug('Formatted TopicAnalyzer results')

        return final_topics_df


    def __complete_topic_assignment_to_tweet_dataframe(self) -> pd.DataFrame:
        """
        Private method to complete the topic assignment to the tweets in the current campaign.

        Returns:
            The complete tweet dataframe with associated topics and T-SNE applied on them.
        """
        # Step 1: Prior data formatting for figure representation
        topic_weights = []

        for _, row_list in enumerate(self.lda_model[self.corpus]):
            topic_weights.append([word for _, word in row_list[0]])

        arr = pd.DataFrame(topic_weights).fillna(0).values
        tsne_model = TSNE(n_components=2, verbose=1, random_state=0, angle=.99, init='pca')
        tsne_lda = tsne_model.fit_transform(arr)

        topic_num = np.argmax(arr, axis=1)

        self.tweet_df['topic'] = topic_num
        self.tweet_df['topic_x_coord'] = tsne_lda[:, 0]
        self.tweet_df['topic_y_coord'] = tsne_lda[:, 1]
        self.tweet_df['topic_tags'] = self.tweet_df.apply(lambda x: self.__map_topic_names(x, self.analysis_results), axis=1)

        return self.tweet_df


    def build_new_results(
            self,
            campaign_analysis_id : int,
            hashtags : Tuple[str, ...] | None = None,
            num_topics : int = 4
        ) -> str:
        """
        Method to carry out topic analysis in the given campaign/s of the XTRACK's engine.

        Args:
            campaign_analysis_id: the identifier with which to store results into the database.
            hashtags: the hashtags with which to filter the activity (if any).
            num_topics: the number of topics to detect in the conversation.

        Returns:
            The average probability per sentiment of the given campaigns and hashtags (if provided).
        """

        # Step 1: Preprocessing data
        self.tweet_df = self.__retrieve_tweets(hashtags)
        tokenized_tweets = self.__preprocess_tweets(self.tweet_df['tweet_text'].to_list())
        lemmatized_tweets = self.__preprocess_tokenized_tweets_to_n_grams_and_lemmas(list(tokenized_tweets))

        # Step 2: Building the LDA Model
        self.lda_model, _, self.corpus = self.__topic_detection(lemmatized_tweets, num_topics)
        self.lda_topics = self.lda_model.show_topics(formatted = False)

        # Step 3: Detecting the dominant topic in each tweet
        topics_df : pd.DataFrame = self.__apply_topic_detection_model(lemmatized_tweets)

        # Step 4: Formatting the results
        self.analysis_results : pd.DataFrame = self.__format_analysis_results(topics_df)

        # Step 5: Complete topic assignment to tweets
        self.__complete_topic_assignment_to_tweet_dataframe()

        # Step 6: Store tweet results into the database
        topic_assignment_df = self.tweet_df.copy()
        topic_assignment_df = topic_assignment_df.drop(axis = 1, columns = ['likes', 'retweets'])
        topic_assignment_df['campaign_analysis_id'] = campaign_analysis_id
        topic_assignment_df['spacy_model_name'] = self.spacy_model_name
        topic_assignment_df = topic_assignment_df[['campaign_analysis_id', 'tweet_text', 'impact', 'topic', 'topic_x_coord', 'topic_y_coord', 'topic_tags', 'spacy_model_name']]
        self.db_connector.store_table_to_sql(topic_assignment_df, 'topic_assignment_analysis_results', 'append')

        # Step 7: Store LDA results into the database
        lda_df = pd.DataFrame(
            data = [(word, proba, topic) for topic, topic_bow in self.lda_model.show_topics(formatted=False) for word, proba in topic_bow],
            columns = ['word', 'probability', 'topic']
        )
        lda_df['campaign_analysis_id'] = campaign_analysis_id
        lda_df['spacy_model_name'] = self.spacy_model_name
        lda_df = lda_df[['campaign_analysis_id', 'word', 'probability', 'topic', 'spacy_model_name']]
        self.db_connector.store_table_to_sql(lda_df, 'lda_topics_analysis_results', 'append')

        return self.analysis_results


    def check_for_pre_computed_results(
            self,
            query : str,
            query_params : Dict[str, Any]
        ) -> Tuple[bool, pd.DataFrame]:
        """
        Method that checks if there exists a previously computed result for the queried campaign/hashtags.

        Args:
            query (str): the query that checks for pre-computed results.
            query_params (Dict[str, Any]): the query parameters to be used.

        Returns:
            A flag indicating if pre-computed results are available together with the pre-computed data.
        """
        self.logger.debug(f'Checking for pre-computed analysis results')

        analysis_df = self.db_connector.retrieve_table_from_sql(
            query_text = query,
            query_params = query_params
        )

        found_precomputed_results = len(analysis_df) > 0

        self.logger.debug(f'Checked for pre-computed analysis results')

        return found_precomputed_results, analysis_df


    def __format_analysis_precomputed_results(self, lda_df : pd.DataFrame) -> Tuple[Tuple[int, Tuple[Tuple[str, float], ...]], ...]:
        """
        Method to format the output of the pre-computed results into the expected format by the front-end.

        Args:
            lda_df (DataFrame): the Pandas DataFrame containing the LDA topics and their word distribution.

        Returns:
            The pre-computed results of the LDA topics in the expected format by the front-end.
        """
        self.logger.debug('Formatting pre-computed results of the TopicAnalyzer (LDAModel)')

        grouped_df = lda_df.groupby('topic')
        formatted_results = [
            (topic, list(zip(group['word'], group['probability'])))
            for topic, group in grouped_df
        ]

        self.logger.debug('Formatted pre-computed results of the TopicAnalyzer (LDAModel)')
        return formatted_results


    def analyze(
            self,
            campaign_analysis_id : int,
            hashtags : Tuple[str, ...] | None = None,
            num_topics : int = 4
        ) -> Any:
        """
        Method to analyze a specific aspect of the given campaign.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            hashtags: the hashtags with which to filter the activity (if any).
            num_topics: the number of topics to detect in the conversation.
        """
        found_tweet_df, pre_computed_tweet_df = self.check_for_pre_computed_results(
            query = self.pre_computed_tweet_df_query,
            query_params = {'campaign_analysis_id' : campaign_analysis_id, 'spacy_model_name' : self.spacy_model_name},
        )

        found_topics_df, pre_computed_topics_df = self.check_for_pre_computed_results(
            query = self.pre_computed_topics_df_query,
            query_params = {'campaign_analysis_id' : campaign_analysis_id, 'spacy_model_name' : self.spacy_model_name},
        )

        if not found_tweet_df and not found_topics_df:
            self.analysis_results = self.build_new_results(campaign_analysis_id, hashtags, num_topics)
        else:
            self.tweet_df = pre_computed_tweet_df
            self.lda_topics = self.__format_analysis_precomputed_results(pre_computed_topics_df)

        return self.analysis_results


    def to_pandas_dataframe(
            self,
            topic_column_name : str = 'topic',
            topic_percentage_contribution_column_name : str = 'topic_contribution_perc',
            topic_keywords_column_name : str = 'topic_keywords',
            representative_text_column_name : str = 'representative_text',
        ) -> pd.DataFrame:
        """
        Method to convert the TopicAnalyzer results to a Pandas DataFrame.

        Args:
            topic_column_name: the name of the column holding the topic being analyzed.
            topic_percentage_contribution_column_name: the name of the column holding the percentage of the tweet that belongs to the topic.
            topic_keywords_column_name: the name of the column holding the keywords of the topic.
            representative_text_column_name: the name of the column holding the most representative tweet of the topic.

        Returns:
            A Pandas DataFrame with the TopicAnalyzer results.
        """
        self.logger.debug('Converting TopicAnalyzer results into a Pandas DataFrame')

        topic_df : pd.DataFrame = self.analysis_results.copy()
        topic_df.columns = [
            topic_column_name,
            topic_percentage_contribution_column_name,
            topic_keywords_column_name,
            representative_text_column_name
        ]

        self.logger.debug('Converted TopicAnalyzer results into a Pandas DataFrame')

        return topic_df


    def tweet_topic_assignment_to_excel(self, output_path : str, sheet_name : str) -> None:
        """
        Method to store the results of the topic assignment to the tweets into a CSV file.

        Args:
            output_path: the path where the Excel file with the results will be stored.
            sheet_name: the name of the excel sheet where the results will be stored.
            *args: the arguments to be used for generating the Pandas DataFrame (if any).
            **kwargs: the keyword arguments to be used for generating the Pandas DataFrame (if any).
        """
        write_mode = 'a' if Path(output_path).is_file() else 'w'

        with pd.ExcelWriter(output_path, engine = 'openpyxl', mode = write_mode) as writer:
            self.tweet_df.to_excel(writer, sheet_name = sheet_name, index = False, header = True)


    def __map_topic_names(self, x, keywords):
        """
        Private method to map topic tags to the topics
        """
        topic_num = x["topic"]
        topic_tag = keywords.loc[keywords['Topic_Num'] == topic_num]['Topic_Keywords'].to_list()[0].split(', ')
        topic_tag = ",".join(topic_tag[:3])

        return f"{topic_num}: {topic_tag}"


    def __to_tsne_map(
            self,
            data : pd.DataFrame,
            width : float = 10,
            height : float = 7,
            x_axis_label : str = 'T-SNE X Axis',
            y_axis_label : str = 'T-SNE Y Axis',
            title : str = '',
            grid : bool = True,
            legend : bool = True,
            x_ticks_rotation : float = 0,
        ) -> Figure:
        """
        Method to visualize the topic results as a 2D T-SNE map.

        Args:
            data (DataFrame): a Pandas DataFrame containing the required information to create the 2D plot.
            width: the width of the image to be created.
            height: the height of the image to be created.
            x_axis_label: the label to be used for the X-axis.
            y_axis_label: the label to be used for the Y-axis.
            title: the title to be used.
            grid: a flag that indicates whether the figure should contain a grid or not.
            legend: a flag that indicates whether the figure should contain a legend or not.
            x_ticks_rotation: the rotation degrees of the X-axis ticks.

        Returns:
            A matplotlib figure with the 2D T-SNE map of the topics.
        """
        self.logger.debug('Creating the 2D T-SNE map of the conversation')

        fig = self.visualizer.create_scatter_plot(
            data = data,
            x_axis_column_name = 'topic_x_coord',
            y_axis_column_name = 'topic_y_coord',
            category_column_name = 'topic_tags',
            width = width,
            height = height,
            x_axis_label = x_axis_label,
            y_axis_label = y_axis_label,
            title = title,
            grid = grid,
            legend = legend,
            x_ticks_rotation = x_ticks_rotation
        )

        self.logger.debug('Created the 2D T-SNE map of the conversation')

        return fig


    def __to_wordcloud(
        self,
        width: float = 10,  # Keep original figure width
        height: float = 7,  # Keep original figure height
        title: str = '',
    ) -> go.Figure:
        """
        Method to convert the TopicAnalyzer results into a figure.

        Args:
            width: the width of the image to be created.
            height: the height of the image to be created.
            title: the title to be used.

        Returns:
            The figure containing the results of the TopicAnalyzer.
        """
        self.logger.debug('Converting word cloud analysis results to image')

        color_maps = [
            LinearSegmentedColormap.from_list("reddish", ["#FF6666", "#CC0000", "#990000"]),
            LinearSegmentedColormap.from_list("greenish", ["#66FF66", "#00CC00", "#009900"]),
            LinearSegmentedColormap.from_list("purplish", ["#DDA0DD", "#BA55D3", "#8A2BE2"]),
            LinearSegmentedColormap.from_list("yellowish", ["#FFFF66", "#FFCC00", "#FF9900"]),
        ]

        topics = self.lda_topics
        num_topics = len(topics)

        fig = make_subplots(
            rows=(num_topics // 2) + 1, 
            cols=2,
            horizontal_spacing=0.01,  # Minimize horizontal spacing
            vertical_spacing=0.2,  # Minimize vertical spacing
        )

        for idx_topic, topic in enumerate(topics):
            _, topic_bow = topic

            cloud = WordCloud(
                stopwords=STOPWORDS,
                background_color='#1a1a2e',
                mode="RGBA",
                width=800,  # Keep word cloud size within original figure size
                height=500,  # Keep word cloud size within original figure size
                max_words=10,
                colormap=color_maps[idx_topic % len(color_maps)],
                prefer_horizontal=1.0
            )

            cloud_i = cloud.generate_from_frequencies(dict(topic_bow), max_font_size=300)
            wordcloud_array = cloud_i.to_array()

            fig.add_trace(
                go.Image(z=wordcloud_array),
                row=(idx_topic // 2) + 1,
                col=(idx_topic % 2) + 1
            )

            fig.update_xaxes(
                showticklabels=False, 
                showgrid=False, 
                zeroline=False, 
                row=(idx_topic // 2) + 1, 
                col=(idx_topic % 2) + 1
            )
            fig.update_yaxes(
                showticklabels=False, 
                showgrid=False, 
                zeroline=False, 
                row=(idx_topic // 2) + 1, 
                col=(idx_topic % 2) + 1
            )

            fig.add_annotation(
                text=f"Topic {idx_topic}",
                xref="x domain",
                yref="y domain",
                x=0.5,
                y=1.5,  # Keep title position closer to the word cloud
                showarrow=False,
                font=dict(size=18, color="#4ecca3"),  # Slightly reduce font size to fit within original figure
                row=(idx_topic // 2) + 1,
                col=(idx_topic % 2) + 1
            )

        fig.update_layout(
            title=title,
            height=height * 80,  # Maintain original figure size
            width=width * 80,  # Maintain original figure size
            plot_bgcolor='#1a1a2e',
            paper_bgcolor='#1a1a2e',
            showlegend=False,
            margin=dict(l=20, r=20, t=100, b=20),  # Reduce margins to allow larger subplots
        )

        self.logger.debug('Converted word cloud analysis results to image')

        return fig


    def __to_bar_plot(
            self,
            width : float = 10,
            height : float = 7,
            color : str = 'lightblue',
            x_axis_label : str = 'Topics',
            y_axis_label : str = 'Tweet Impact',
            title : str = 'Tweet impact distribution per topic',
            grid : bool = True,
            x_ticks_rotation : float = 0
        ) -> go.Figure:
        """
        Method to convert the TopicAnalyzer results into a figure.

        Args:
            width: the width of the image to be created.
            height: the height of the image to be created.
            color: the color to be used for the barplot.
            x_axis_label: the label to be used for the X-axis.
            y_axis_label: the label to be used for the Y-axis.
            title: the title to be used.
            grid: a flag that indicates whether the figure should contain a grid or not.
            x_ticks_rotation: the rotation degrees of the X-axis ticks.

        Returns:
            The figure containing the results of the TopicAnalyzer.
        """
        self.logger.debug('Converting topic impact activity analysis results to image')

        data_df = self.tweet_df.groupby('topic')['impact'].count().sort_values(ascending=False)[:20].to_frame().reset_index()
        data_df['topic'] = data_df['topic'].astype(str)

        fig = self.visualizer.create_bar_plot(
            data = data_df,
            x_axis_column_name = 'topic',
            y_axis_column_name = 'impact',
            width = width,
            height = height,
            color = color,
            x_axis_label = x_axis_label,
            y_axis_label = y_axis_label,
            title = title,
            grid = grid,
            x_ticks_rotation = x_ticks_rotation
        )

        self.logger.debug('Converted topic impact analysis results to image')

        return fig


    def to_image(
            self,
            fig_type : Literal['t-sne', 'wordcloud', 'barplot'],
            width : float = 10,
            height : float = 7,
            t_sne_fig_kwargs : Dict[str, Any] = {},
            barplot_fig_kwargs : Dict[str, Any] = {},
            wordcloud_fig_kwargs : Dict[str, Any] = {},
        ) -> Figure:
        """
        Method to convert the TopicAnalyzer results into a figure.

        Args:
            fig_type: the type of figure to be created (a 2D T-SNE, a bar plot with topic impact or a wordcloud).
            width: the width of the image to be created.
            height: the height of the image to be created.
            t_sne_fig_kwargs: the arguments to be used for the 2D T-SNE conversation plot.
            barplot_fig_kwargs: the arguments to be used for the topic impact barplot.
            wordcloud_fig_kwargs: the arguments to be used for the topic wordcloud plot.

        Returns:
            The figure containing the results of the TopicAnalyzer.
        """
        self.logger.debug('Converting topic analysis results to image')

        
        # Step 2: Creating the specified image
        match fig_type:
            case 't-sne':
                fig = self.__to_tsne_map(
                    data = self.tweet_df,
                    width = width,
                    height = height,
                    **t_sne_fig_kwargs
                )
            case 'wordcloud':
                fig = self.__to_wordcloud(
                    width = width,
                    height = height,
                    **wordcloud_fig_kwargs
                )
            case 'barplot':
                fig = self.__to_bar_plot(
                    width = width,
                    height = height,
                    **barplot_fig_kwargs
                )

        self.logger.debug('Converted topic analysis results to image')

        return fig
