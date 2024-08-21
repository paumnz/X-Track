import { create_bar_plot } from './utils.js';
import { create_line_plot } from './utils.js';


export function show_user_analysis(sessionData) {

    // Retrieving canvas and visualization elements
    const accountCreationCanvas = document.getElementById('cv_account_creation');
    const influentialUsersCanvas = document.getElementById('cv_influential_users');

    // Plotting the information
    create_line_plot(sessionData.user_analysis['account_creation'], accountCreationCanvas)
    create_bar_plot(sessionData.user_analysis['influential_users'], influentialUsersCanvas)
}