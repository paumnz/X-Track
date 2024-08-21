import { plotGraph, create_multiline_plot } from './utils.js';


export function show_network_metric_analysis(sessionData) {

    // Retrieving canvas and visualization elements
    const retweetNetworkDiv = document.getElementById('cv_retweet_network_graph')
    const retweetNetworkCanvas = document.getElementById('cv_retweet_network')
    const replyNetworkDiv = document.getElementById('cv_reply_network_graph')
    const replyNetworkCanvas = document.getElementById('cv_reply_network')

    // Plotting network metric results
    create_multiline_plot(sessionData.network_metric_analysis['retweet_network_metrics'], retweetNetworkCanvas)
    create_multiline_plot(sessionData.network_metric_analysis['reply_network_metrics'], replyNetworkCanvas)

    // Plotting retweet network
    const retweet_edges = sessionData.network_metric_analysis['retweet_network']['edges']
    const retweet_sentiment_dict = sessionData.network_metric_analysis['retweet_network']['sentiment']
    const retweet_activity_dict = sessionData.network_metric_analysis['retweet_network']['activity']
    plotGraph(retweet_edges, retweet_sentiment_dict, retweet_activity_dict, retweetNetworkDiv);

    // Plotting reply network
    const reply_edges = sessionData.network_metric_analysis['reply_network']['edges']
    const reply_sentiment_dict = sessionData.network_metric_analysis['reply_network']['sentiment']
    const reply_activity_dict = sessionData.network_metric_analysis['reply_network']['activity']
    plotGraph(reply_edges, reply_sentiment_dict, reply_activity_dict, replyNetworkDiv);
}
    