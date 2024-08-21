import { create_bar_plot, create_line_plot, create_pie_chart } from './utils.js';


export function show_user_analysis(sessionData) {

    // Retrieving canvas and visualization elements
    const accountCreationCanvas = document.getElementById('cv_account_creation');
    const influentialUsersCanvas = document.getElementById('cv_influential_users');
    const botUsersCanvas = document.getElementById('cv_bot_users');

    // Plotting the information
    create_line_plot(sessionData.user_analysis['account_creation'], accountCreationCanvas)
    create_bar_plot(sessionData.user_analysis['influential_users'], influentialUsersCanvas)
    create_pie_chart(sessionData.user_analysis['bot_users'], botUsersCanvas, '', 0)
}