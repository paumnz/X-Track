import { create_bar_plot } from './utils.js';


export function show_speech_analysis(sessionData) {

    // Retrieving canvas and visualization elements
    const sentimentCanvas = document.getElementById('cv_sentiment');
    const emotionCanvas = document.getElementById('cv_emotion');
    const liwcCanvas = document.getElementById('cv_liwc');


    // Plotting the information
    create_bar_plot(sessionData.speech_analysis['sentiment'], sentimentCanvas)
    create_bar_plot(sessionData.speech_analysis['emotion'], emotionCanvas)
    // create_bar_plot(sessionData.speech_analysis['liwc'], liwcCanvas)
}