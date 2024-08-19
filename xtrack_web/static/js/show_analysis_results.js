import { getSessionData } from './utils.js';
import { show_motto_analysis } from './motto_analysis.js';
import { show_media_analysis } from './media_analysis.js';
import { show_user_analysis } from './user_analysis.js';
import { show_tweet_analysis } from './tweet_analysis.js';

getSessionData()
.then(sessionData => {
    sessionData = sessionData.analysis_result

    // // 1. Motto Analysis
    // show_motto_analysis(sessionData)

    // // 2. Media analysis
    // show_media_analysis(sessionData)

    // // 3. User analysis
    // show_user_analysis(sessionData)

    // 4. Tweet analysis
    show_tweet_analysis(sessionData)

    return sessionData
})
.catch(error => {
    console.log('Error:', error);
    return undefined
})
