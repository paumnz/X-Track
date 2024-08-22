import { create_plotly_figure, create_plotly_figure_subplots, create_bar_plot } from './utils.js';


export function show_topic_analysis(sessionData) {

    // Retrieving canvas and visualization elements
    const topicWordcloudCanvas = 'cv_topic_wordcloud';
    const tsneCanvas = 'cv_topic_t_sne';
    const topicImpactCanvas = document.getElementById('cv_topic_impact')

    // Converting JSON string to JSON
    sessionData.topic_analysis['topic_wordcloud'] = JSON.parse(sessionData.topic_analysis['topic_wordcloud'])
    sessionData.topic_analysis['t_sne'] = JSON.parse(sessionData.topic_analysis['t_sne'])

    // Plotting the information
    create_plotly_figure_subplots('', sessionData.topic_analysis['topic_wordcloud'], topicWordcloudCanvas, 250, false)
    create_bar_plot(sessionData.topic_analysis['topic_impact'], topicImpactCanvas)
    create_plotly_figure('', sessionData.topic_analysis['t_sne'], tsneCanvas, 500, true)
}