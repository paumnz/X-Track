import { create_line_plot, create_biline_plot, create_pie_chart, create_plotly_figure, createTable } from './utils.js';


export function show_tweet_analysis(sessionData) {

    // Retrieving canvas and visualization elements
    const entityTreeMapDiv = 'cv_tweet_entity_tree_map';
    const wordcloudDiv = 'cv_tweet_word_cloud';
    const tweetCreationCanvas = document.getElementById('cv_tweet_creation')
    const tweetCreationSentimentCanvas = document.getElementById('cv_tweet_creation_per_sentiment')
    const tweetLanguageCanvas = document.getElementById('cv_tweet_language')
    const tweetImpactTable = document.getElementById('table_tweet_impact')
    const tweetDuplicationTable = document.getElementById('table_tweet_duplication')

    // Parsing JSON data from Plotly
    sessionData.tweet_analysis['entity_tree_map'] = JSON.parse(sessionData.tweet_analysis['entity_tree_map'])
    sessionData.tweet_analysis['word_cloud'] = JSON.parse(sessionData.tweet_analysis['word_cloud'])

    // Plotting results
    create_line_plot(sessionData.tweet_analysis['tweet_creation_time'], tweetCreationCanvas, '', 4)
    create_biline_plot(sessionData.tweet_analysis['tweet_creation_time_per_sentiment'], tweetCreationSentimentCanvas, 'x_values_pos', 'y_values_pos', 'x_values_neg', 'y_values_neg', 'Positive tweets', 'Negative tweets', 4, true)
    create_plotly_figure('Tweet entity tree map', sessionData.tweet_analysis['entity_tree_map'], entityTreeMapDiv)
    create_plotly_figure('', sessionData.tweet_analysis['word_cloud'], wordcloudDiv, 350, false)
    create_pie_chart(sessionData.tweet_analysis['tweet_language'], tweetLanguageCanvas)
    createTable(sessionData.tweet_analysis['tweet_impact'], tweetImpactTable)
    createTable(sessionData.tweet_analysis['tweet_duplication'], tweetDuplicationTable)
}