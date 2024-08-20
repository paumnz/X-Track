import { create_multiline_plot } from './utils.js';


export function show_network_metric_analysis(sessionData) {

    // Retrieving canvas and visualization elements
    const retweetNetworkCanvas = document.getElementById('cv_retweet_network')
    const replyNetworkCanvas = document.getElementById('cv_reply_network')

    // Plotting results
    create_multiline_plot(sessionData.network_metric_analysis['retweet_network_metrics'], retweetNetworkCanvas)
    create_multiline_plot(sessionData.network_metric_analysis['reply_network_metrics'], replyNetworkCanvas)
}