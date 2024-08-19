import { create_bar_plot } from './utils.js';


export function show_media_analysis(sessionData) {

    // Retrieving canvas and visualization elements
    const domainCanvas = document.getElementById('cv_domain');
    const headlineCanvas = document.getElementById('cv_headline');

    // Plotting the information
    create_bar_plot(sessionData.media_analysis['domains'], domainCanvas)
    create_bar_plot(sessionData.media_analysis['headlines'], headlineCanvas)
}