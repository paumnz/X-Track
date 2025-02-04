"""
Module to implement the back-end application that serves the front-end and resolves the API calls.
"""


import configparser
import json
from datetime import datetime
from typing import Any, Dict, Tuple

import numpy as np
import plotly
from flask import Flask, render_template, request, url_for, jsonify, session
from flask_session import Session
from pandas import DataFrame

from xtrack_engine.bot_analysis.bot_analyzer import BotAnalyzer
from xtrack_engine.database_connection.db_connector import DBConnector
from xtrack_engine.motto_analysis.motto_analyzer import MottoAnalyzer
from xtrack_engine.media_analysis.domain_analyzer import DomainAnalyzer
from xtrack_engine.media_analysis.headline_analyzer import HeadlineAnalyzer
from xtrack_engine.network_analysis.network_analyzer import NetworkAnalyzer
from xtrack_engine.network_analysis.network_metric_analyzer import NetworkMetricAnalyzer
from xtrack_engine.sentiment_analysis.emotion_analyzer import EmotionAnalyzer
from xtrack_engine.sentiment_analysis.liwc_analyzer import LIWCAnalyzer
from xtrack_engine.sentiment_analysis.sentiment_analyzer import SentimentAnalyzer
from xtrack_engine.topic_analysis.topic_analyzer import TopicAnalyzer
from xtrack_engine.tweet_analysis.tweet_entity_analyzer import TweetEntityAnalyzer
from xtrack_engine.tweet_analysis.tweet_creation_time_analyzer import TweetCreationTimeAnalyzer
from xtrack_engine.tweet_analysis.tweet_sentiment_creation_time_analyzer import TweetSentimentCreationTimeAnalyzer
from xtrack_engine.tweet_analysis.tweet_language_analyzer import TweetLanguageAnalyzer
from xtrack_engine.tweet_analysis.tweet_redundancy_analyzer import TweetRedundancyAnalyzer
from xtrack_engine.tweet_analysis.word_cloud_analyzer import WordCloudAnalyzer
from xtrack_engine.tweet_analysis.tweet_impact_analyzer import TweetImpactAnalyzer
from xtrack_engine.twitter_data_ingestor.query_builder import TrendingTopicsManager
from xtrack_engine.twitter_data_ingestor.query_downloader import TwitterDataIngestion
from xtrack_engine.twitter_data_ingestor.sql_converter import DataMigration
from xtrack_engine.user_analysis.account_creation_analyzer import AccountCreationAnalyzer
from xtrack_engine.user_analysis.multi_criteria_user_analyzer import MultiCriteriaUserAnalyzer


XTRACK_CONFIGURATION_FILEPATH = '../config.ini'



app = Flask(__name__)

# Configuring the session
config_parser = configparser.ConfigParser()
config_parser.read(XTRACK_CONFIGURATION_FILEPATH)

app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = config_parser.get('front-end', 'app_secret_key')
Session(app)


@app.route('/')
def serve_frontend():
    """
    Method to serve the front-end of the web application
    """
    session['analysis_result'] = {}

    return render_template('index.html')


def _motto_analysis(campaigns : Tuple[str, ...], db_conn : DBConnector, campaign_analysis_id : int) -> Dict[str, Any]:
    """
    Method to carry out the motto analysis

    Args:
        campaigns (Tuple[str, ...]): the campaign/s to be analyzed.
        db_conn (DBConnector): the database connector instance to be used.
        campaign_analysis_id (int): the identifier to use for retrieving/storing the analysis results.

    Returns:
        A dictionary with the motto analysis results to be shown in the front-end.
    """
    top_k_mottos = MottoAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {'sentiment' : 'both'}, {'sentiment' : 'both', 'top_k' : 10})
    top_k_negative_mottos = MottoAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {'sentiment' : 'negative'}, {'sentiment' : 'negative', 'top_k' : 10})
    top_k_positive_mottos = MottoAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {'sentiment' : 'positive'}, {'sentiment' : 'positive', 'top_k' : 10})

    return {
        'all' : {
            'labels' : [label for label, _ in top_k_mottos],
            'data' : [label_usage for _, label_usage in top_k_mottos]
        },
        'negative' : {
            'labels' : [label for label, _ in top_k_negative_mottos],
            'data' : [label_usage for _, label_usage in top_k_negative_mottos]
        },
        'positive' : {
            'labels' : [label for label, _ in top_k_positive_mottos],
            'data' : [label_usage for _, label_usage in top_k_positive_mottos]
        }
    }


def _media_analysis(
        campaigns : Tuple[str, ...],
        hashtags : Tuple[str, ...],
        db_conn : DBConnector,
        campaign_analysis_id : int
    ) -> Dict[str, Any]:
    """
    Method to carry out the media outlet analysis

    Args:
        campaigns (Tuple[str, ...]): the campaign/s to be analyzed.
        hashtags (Tuple[str, ...]): the hashtags with which to filter user activity.
        db_conn (DBConnector): the database connector instance to be used.
        campaign_analysis_id (int): the identifier to use for retrieving/storing the analysis results.

    Returns:
        A dictionary with the media outlet analysis results to be shown in the front-end.
    """
    top_k_domains = DomainAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, new_computation_kwargs = {'top_k' : 10, 'hashtags' : hashtags})
    top_k_headlines = HeadlineAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, new_computation_kwargs = {'top_k' : 10, 'hashtags' : hashtags})

    return {
        'domains' : {
            'labels' : [label for label, _ in top_k_domains],
            'data' : [label_usage for _, label_usage in top_k_domains]
        },
        'headlines' : {
            'labels' : [label for label, _ in top_k_headlines],
            'data' : [label_usage for _, label_usage in top_k_headlines]
        }
    }


def _user_analysis(
        campaigns : Tuple[str, ...],
        hashtags : Tuple[str, ...],
        db_conn : DBConnector,
        campaign_analysis_id : int,
        top_k : int = 10
    ) -> Dict[str, Any]:
    """
    Method to carry out the user analysis.

    Args:
        campaigns (Tuple[str, ...]): the campaign/s to be analyzed.
        hashtags (Tuple[str, ...]): the hashtags with which to filter user activity.
        db_conn (DBConnector): the database connector instance to be used.
        campaign_analysis_id (int): the identifier with which to store or restore computed results.
        top_k (int): the number of influential users to be retrieved.

    Returns:
        A dictionary with the user analysis results to be shown in the front-end.
    """

    # Step 1: Account creation analysis
    account_creation_analysis = AccountCreationAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {}, {'hashtags' : hashtags})

    # Step 2: Influential users analysis
    influential_users = MultiCriteriaUserAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {}, {'top_k' : top_k, 'hashtags' : hashtags})

    # Step 3: Bot analysis
    bot_analysis = BotAnalyzer(campaigns, db_conn, XTRACK_CONFIGURATION_FILEPATH).analyze(campaign_analysis_id, {}, {'hashtags' : hashtags, 'top_k' : None})

    return {
        'account_creation' : {
            'x_values' : [x_value for x_value in account_creation_analysis['month']],
            'y_values' : [y_value for y_value in account_creation_analysis['accounts']]
        },
        'influential_users' : {
            'labels' : [label for label, _ in influential_users],
            'data' : [label_usage for _, label_usage in influential_users]
        },
        'bot_users' : {
            'labels' : [label for label in bot_analysis['bot']],
            'values' : [frequency for frequency in bot_analysis['frequency']]
        }
    }


def _tweet_analysis(
        campaigns : Tuple[str, ...],
        hashtags : Tuple[str, ...],
        db_conn : DBConnector,
        campaign_analysis_id : int,
        top_k : int = 10
    ) -> Dict[str, Any]:
    """
    Method to carry out the tweet analysis.

    Args:
        campaigns (Tuple[str, ...]): the campaign/s to be analyzed.
        hashtags (Tuple[str, ...]): the hashtags with which to filter user activity.
        db_conn (DBConnector): the database connector instance to be used.
        campaign_analysis_id (int): the identifier to store or restore computed analysis results.
        top_k (int): the number to be used for top-N rankings.

    Returns:
        A dictionary with the tweet analysis results to be shown in the front-end.
    """

    # Step 1: Tweet entity analyzer
    tweet_entity_analyzer = TweetEntityAnalyzer(campaigns, db_conn)
    tweet_entity_analyzer.analyze(campaign_analysis_id, {}, {'top_k' : top_k, 'hashtags' : hashtags})
    tweet_entities_fig = tweet_entity_analyzer.to_image(title = 'Tweet entity tree map')

    # Step 2: Tweet creation time analyzer
    tweet_creation_time_analysis = TweetCreationTimeAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {}, {'hashtags' : hashtags})

    # Step 3: Tweet creation time per sentiment analyzer
    tweet_creation_time_per_sentiment_analysis = TweetSentimentCreationTimeAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {}, {'hashtags' : hashtags})

    # Step 4: Wordcloud analyzer
    wordcloud_analyzer = WordCloudAnalyzer(campaigns, db_conn)
    wordcloud_analyzer.analyze(campaign_analysis_id, {}, {'hashtags' : hashtags})
    wordcloud_fig = wordcloud_analyzer.to_image()

    # Step 5: Language analyzer
    tweet_language_analysis = TweetLanguageAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {}, {'top_k' : 5, 'hashtags' : hashtags})

    # Step 6: Tweet impact analyzer
    tweet_impact_analysis = TweetImpactAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {'tweet_impact_mode' : 'retweet'}, {'top_k' : top_k, 'hashtags' : hashtags, 'mode' : 'retweet'})

    # Step 7: Tweet impact analyzer
    tweet_redundancy_analysis = TweetRedundancyAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {}, {'top_k' : top_k, 'hashtags' : hashtags})

    return {
        'entity_tree_map' : json.dumps(tweet_entities_fig, cls = plotly.utils.PlotlyJSONEncoder),
        'tweet_creation_time' : {
            'x_values' : [day_hour for day_hour in tweet_creation_time_analysis['dayhour']],
            'y_values' : [tweet_volume for tweet_volume in tweet_creation_time_analysis['tweet_volume']],
        },
        'tweet_creation_time_per_sentiment' : {
            'x_values_pos' : [day_hour for day_hour in tweet_creation_time_per_sentiment_analysis[tweet_creation_time_per_sentiment_analysis['sentiment'] == 'positive']['dayhour']],
            'y_values_pos' : [tweet_volume for tweet_volume in tweet_creation_time_per_sentiment_analysis[tweet_creation_time_per_sentiment_analysis['sentiment'] == 'positive']['tweet_volume']],
            'x_values_neg' : [day_hour for day_hour in tweet_creation_time_per_sentiment_analysis[tweet_creation_time_per_sentiment_analysis['sentiment'] == 'negative']['dayhour']],
            'y_values_neg' : [tweet_volume for tweet_volume in tweet_creation_time_per_sentiment_analysis[tweet_creation_time_per_sentiment_analysis['sentiment'] == 'negative']['tweet_volume']],
        },
        'word_cloud' : json.dumps(wordcloud_fig, cls = plotly.utils.PlotlyJSONEncoder),
        'tweet_language' : {
            'labels' : [language for language in tweet_language_analysis['language']],
            'values' : [tweet_volume for tweet_volume in tweet_language_analysis['tweet_volume']],
        },
        'tweet_impact' : [[row['tweet'], row['user'], row['impact']] for _, row in tweet_impact_analysis.iterrows()],
        'tweet_duplication' : [[row['tweet'], row['user'], row['frequency']] for _, row in tweet_redundancy_analysis.iterrows()],
    }


def _prepare_network_metric_results(network_metric_df : DataFrame, metric_names : Tuple[str, ...]) -> Dict[str, Any]:
    """
    Functionn to prepare network metric results in the expected format by the front-end.

    Args:
        network_metric_df (DataFrame): the pandas DataFrame containing the network metrics results.
        metric_names (Tuple[str, ...]): the name of the metrics that will be computed.
    Returns:
        A dictionary in the expected format by the front-end to show the results.
    """
    metric_analysis_results : Dict[str, Any] = {'x_values' : network_metric_df['date'].apply(lambda row: datetime.strftime(row, '%Y-%m-%d')).to_list(), 'y_values' : [], 'metrics' : metric_names}

    for metric in metric_names:
        metric_analysis_results['y_values'].append(network_metric_df[metric].to_list())

    return metric_analysis_results


def _prepare_network_results(network_df : DataFrame) -> Dict[str, Any]:
    """
    Function to prepare network data in the expected format by the front-end.

    Args:
        network_df (DataFrame): the DataFrame with the network analysis results.

    Returns:
        The given network in the front-end's format.
    """
    network_edge_results = []
    sentiment_dict_results = {}
    activity_dict_results = {}

    # Step 1: Preparing the edges
    for _, row in network_df.iterrows():
        network_edge_results.append(
            {
                'from' : row['source'],
                'to' : row['target'],
                'value' : row['weight']
            }
        )

    # Step 2: Preparing the sentiment dictionary
    source_sentiment_df = network_df[['source', 'source_sentiment']]
    target_sentiment_df = network_df[['target', 'target_sentiment']]
    sentiment_data = np.vstack([source_sentiment_df.values, target_sentiment_df.values])

    for row in sentiment_data:
        sentiment_dict_results[str(row[0])] = float(row[1])

    # Step 3: Preparing the activity dictionary
    source_activity_df = network_df[['source', 'source_activity']]
    target_activity_df = network_df[['target', 'target_activity']]
    activity_data = np.vstack([source_activity_df.values, target_activity_df.values])

    for row in activity_data:
        activity_dict_results[str(row[0])] = float(row[1])

    return {
        'edges' : network_edge_results,
        'sentiment' : sentiment_dict_results,
        'activity' : activity_dict_results
    }


def _network_metric_analysis(
        campaigns : Tuple[str, ...],
        hashtags : Tuple[str, ...],
        db_conn : DBConnector,
        network_metrics : Tuple[str, ...],
        campaign_analysis_id : int
    ) -> Dict[str, Any]:
    """
    Method to carry out the network metric analysis.

    Args:
        campaigns (Tuple[str, ...]): the campaign/s to be analyzed.
        hashtags (Tuple[str, ...]): the hashtags with which to filter user activity.
        db_conn (DBConnector): the database connector instance to be used.
        network_metrics (Tuple[str, ...]): the network metrics to be computed.
        campaign_analysis_id (int): the identifier to be used for storing/restoring the computed results.

    Returns:
        A dictionary with the network metric analysis results to be shown in the front-end.
    """

    # Step 1: Analyzing network metrics over time
    retweet_network_metrics = NetworkMetricAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {'network_metrics' : network_metrics, 'network_type' : 'retweet'}, {'network_metrics' : network_metrics, 'hashtags' : hashtags, 'network_type' : 'retweet'})
    reply_network_metrics = NetworkMetricAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {'network_metrics' : network_metrics, 'network_type' : 'reply'}, {'network_metrics' : network_metrics, 'hashtags' : hashtags, 'network_type' : 'reply'})

    # Step 2: Preparing results
    retweet_network_metrics_analysis_results = _prepare_network_metric_results(retweet_network_metrics, network_metrics)
    reply_network_metrics_analysis_results = _prepare_network_metric_results(reply_network_metrics, network_metrics)

    # Step 3: Creating both networks for plotting
    retweet_network_df = NetworkAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {'network_type' : 'retweet'}, {'hashtags' : hashtags, 'network_type' : 'retweet'})
    retweet_network_analysis_results = _prepare_network_results(retweet_network_df)
    reply_network_df = NetworkAnalyzer(campaigns, db_conn).analyze(campaign_analysis_id, {'network_type' : 'reply'}, {'hashtags' : hashtags, 'network_type' : 'reply'})
    reply_network_analysis_results = _prepare_network_results(reply_network_df)

    return {
        'retweet_network_metrics' : retweet_network_metrics_analysis_results,
        'reply_network_metrics' : reply_network_metrics_analysis_results,
        'retweet_network' : retweet_network_analysis_results,
        'reply_network' : reply_network_analysis_results,
    }


def _prepare_speech_analysis_results(
        speech_df : DataFrame,
        category_column : str,
        value_column : str,
        top_k : int = 10
    ) -> Dict[str, Any]:
    """
    Function to prepare the speech analysis results into the format expected at the front-end.

    Args:
        speech_df (DataFrame): the Pandas DataFrame containing the speech analysis results.
        category_column (str): the column holding each of the categories analyzed.
        value_column (str): the column holding the values of each of the categories.
        top_k (int): the number of most frequently used speech categories.

    Returns:
        A dictionary in the format expected by the front-end.
    """
    labels = speech_df[category_column].to_list()[:top_k]
    values = speech_df[value_column].to_list()[:top_k]

    return {
        'labels' : labels,
        'data' : values,
    }


def _speech_analysis(
        campaigns : Tuple[str, ...],
        hashtags : Tuple[str, ...],
        db_conn : DBConnector,
        language : str,
        campaign_analysis_id : int,
    ) -> Dict[str, Any]:
    """
    Method to carry out the speech analysis

    Args:
        campaigns (Tuple[str, ...]): the campaign/s to be analyzed.
        hashtags (Tuple[str, ...]): the hashtags with which to filter user activity.
        db_conn (DBConnector): the database connector instance to be used.
        language (str): the language to be used for sentiment and emotion detection.
        campaign_analysis_id (int): the identifier to store/restore the computed results.

    Returns:
        A dictionary with the media outlet analysis results to be shown in the front-end.
    """

    # Step 1: Sentiment analysis
    sentiment_df = SentimentAnalyzer(campaigns, db_conn, language = language).analyze(campaign_analysis_id, {'language' : language}, {'hashtags' : hashtags})
    sentiment_analysis = _prepare_speech_analysis_results(sentiment_df, 'sentiment', 'probability')

    # Step 2: Emotion analysis
    emotion_df = EmotionAnalyzer(campaigns, db_conn, language = language).analyze(campaign_analysis_id, {'language' : language}, {'hashtags' : hashtags})
    emotion_analysis = _prepare_speech_analysis_results(emotion_df, 'emotion', 'probability')

    # # Step 3: Emotion analysis
    # liwc_dict = config_parser.get('liwc', 'liwc_dict_filepath')
    # liwc_df = LIWCAnalyzer(campaigns, db_conn, liwc_dict_filepath = liwc_dict).analyze(campaign_analysis_id, {'liwc_dict' : liwc_dict}, {'hashtags' : hashtags})
    # liwc_df = liwc_df.sort_values(by = 'frequency', ascending = False)
    # liwc_analysis = _prepare_speech_analysis_results(liwc_df, 'liwc_category', 'frequency')

    return {
        'sentiment' : sentiment_analysis,
        'emotion' : emotion_analysis,
        # 'liwc' : liwc_analysis
    }


def _topic_analysis(
        campaigns : Tuple[str, ...],
        hashtags : Tuple[str, ...],
        db_conn : DBConnector,
        language : str,
        campaign_analysis_id : int
    ) -> Dict[str, Any]:
    """
    Method to carry out the topic analysis

    Args:
        campaigns (Tuple[str, ...]): the campaign/s to be analyzed.
        hashtags (Tuple[str, ...]): the hashtags with which to filter user activity.
        db_conn (DBConnector): the database connector instance to be used.
        language (str): the language to be used for the topic analysis.
        campaign_analysis_id (int): the identifier with which to store/restore the computed results.

    Returns:
        A dictionary with the topic analysis results to be shown in the front-end.
    """
    topic_analyzer = TopicAnalyzer(campaigns, db_conn, language = language)
    topic_analyzer.analyze(campaign_analysis_id, hashtags)

    # Step 1: Plotting the wordcloud per topic
    wordcloud_fig = topic_analyzer.to_image('wordcloud')

    # Step 2: Plotting the 2D T-SNE
    tsne_fig = topic_analyzer.to_image('t-sne')

    # Step 3: Retrieving topic impact analysis
    topic_impact_df = topic_analyzer.tweet_df.groupby('topic')['impact'].count().sort_values(ascending=False)[:20].to_frame().reset_index()
    topic_impact_df['topic'] = topic_impact_df['topic'].astype(str)

    return {
        't_sne' : json.dumps(tsne_fig, cls = plotly.utils.PlotlyJSONEncoder),
        'topic_wordcloud' : json.dumps(wordcloud_fig, cls = plotly.utils.PlotlyJSONEncoder),
        'topic_impact' : {
            'labels' : [f'Topic {topic}' for topic in topic_impact_df['topic']],
            'data' : [impact_value for impact_value in topic_impact_df['impact']]
        }
    }


@app.route('/analyze', methods=['POST'])
def analyze_campaigns():
    """
    Method to analyze one or more campaigns using the XTRACK's framework.
    """

    # Step 1: Retrieving POST request data
    data = request.get_json()
    campaigns = data.get('campaigns')
    hashtags = tuple(data.get('hashtags').replace(' ', '').split(','))
    hashtags = None if len(hashtags) == 1 and hashtags[0] == '' else hashtags
    language = data.get('language')
    language = 'en' if language == '' or language is None else language
    network_metrics = tuple(data.get('network_metrics').split(', '))
    network_metrics = ('efficiency', 'density', 'modularity') if len(network_metrics) == 1 and network_metrics[0] == '' else network_metrics

    # Step 2: Resetting session results (if any)
    session['analysis_result'] = {}

    # Step 3: Preparing the campaign analysis results (in case we can avoid computations)
    db_conn = DBConnector(XTRACK_CONFIGURATION_FILEPATH)

    campaign_analysis_stored_results = db_conn.check_existing_results(campaigns, hashtags)
    if not campaign_analysis_stored_results[0]:
        db_conn.insert_new_results_row(campaign_analysis_stored_results[1], campaigns, hashtags)

    # Step 4: Applying an analysis
    analysis_result = {}

    analysis_result['speech_analysis'] = _speech_analysis(campaigns, hashtags, db_conn, language, campaign_analysis_stored_results[1]) # Must go first
    analysis_result['motto_analysis'] = _motto_analysis(campaigns, db_conn, campaign_analysis_stored_results[1])
    analysis_result['media_analysis'] = _media_analysis(campaigns, hashtags, db_conn, campaign_analysis_stored_results[1])
    analysis_result['user_analysis'] = _user_analysis(campaigns, hashtags, db_conn, campaign_analysis_stored_results[1])
    analysis_result['tweet_analysis'] = _tweet_analysis(campaigns, hashtags, db_conn, campaign_analysis_stored_results[1])
    analysis_result['network_metric_analysis'] = _network_metric_analysis(campaigns, hashtags, db_conn, network_metrics, campaign_analysis_stored_results[1])
    analysis_result['topic_analysis'] = _topic_analysis(campaigns, hashtags, db_conn, language, campaign_analysis_stored_results[1])

    session['analysis_result'] = analysis_result

    # Step 5: Redirecting the front-end to the results page
    return jsonify({'redirect': url_for('result')})


@app.route('/ingest', methods=['POST'])
def ingest_twitter_data():
    """
    Method to ingest Twitter data to be analyzed with XTRACK's framework.
    """

    # Step 1: Retrieving the configurations
    mongo_uri = config_parser.get('mongo-db', 'mongo_uri')
    mongo_db = config_parser.get('mongo-db', 'mongo_db')
    default_collection = config_parser.get('mongo-db', 'default_collection')
    tweet_collection = config_parser.get('mongo-db', 'tweet_collection')
    user_collection = config_parser.get('mongo-db', 'user_collection')
    twitter_bearer_token = config_parser.get('twitter-api', 'bearer_token')
    twitter_daily_tweet_limit = config_parser.get('twitter-api', 'daily_tweet_limit')
    sql_host = config_parser.get('database', 'host')
    sql_port = config_parser.get('database', 'port')
    sql_database = config_parser.get('database', 'db_name')
    sql_username = config_parser.get('database', 'username')
    sql_password = config_parser.get('database', 'password')

    # Step 2: Retrieving the query from the user
    data = request.get_json()
    start_date = data.get('start_date')
    trending_topics = data.get('trending_topics').replace(' ', '').split(',')
    city = data.get('city')
    days = int(data.get('days'))
    campaign = data.get('campaign')

    # Step 3: Managing the trending topics
    trending_topic_manager = TrendingTopicsManager(start_date, trending_topics, mongo_uri, mongo_db, default_collection, city)
    trending_topic_manager.insert_trending_topics(days = days)

    # Step 4: Managing data download to MongoDB
    data_downloader = TwitterDataIngestion(campaign, twitter_bearer_token, twitter_daily_tweet_limit, mongo_uri, mongo_db, default_collection, tweet_collection, user_collection)
    data_downloader.fetch_and_store_tweets()

    # Step 5: Manading data migration from MongoDB to MySQL
    sql_migrator = DataMigration(mongo_uri, mongo_db, default_collection, {'host' : sql_host, 'port' : sql_port, 'username' : sql_username, 'password' : sql_password, 'database' : sql_database})
    sql_migrator.process_tweets()

    # Step 5: Redirecting the front-end to the results page
    return jsonify({'redirect': url_for('serve_frontend')})


@app.route('/result')
def result():
    """
    Method to display the results page
    """

    # Retrieve session data
    result = session.get('analysis_result', None)

    return render_template('result.html', result = result)


@app.route('/get_session')
def get_session():
    """
    Method to retrieve session data
    """
    if 'analysis_result' in session:
        return {'analysis_result': session['analysis_result']}
    return {'analysis_result': None}


@app.route('/data_analysis')
def data_analysis():
    """
    Method to display the results page
    """
    return render_template('data_analysis.html')


@app.route('/data_download')
def data_download():
    """
    Method to display the results page
    """
    return render_template('data_download.html')


if __name__ == '__main__':
    app.run(debug=True)

