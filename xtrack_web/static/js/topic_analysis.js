import { create_plotly_figure_subplots } from './utils.js';


export function show_topic_analysis(sessionData) {

    // Retrieving canvas and visualization elements
    const topicWordcloudCanvas = 'cv_topic_wordcloud';

    // Converting JSON string to JSON
    sessionData.topic_analysis['topic_wordcloud'] = JSON.parse(sessionData.topic_analysis['topic_wordcloud'])

    // Plotting the information
    create_plotly_figure_subplots('', sessionData.topic_analysis['topic_wordcloud'], topicWordcloudCanvas, 250, false)
}