import { getSessionData } from './utils.js';
import { show_motto_analysis } from './motto_analysis.js';
import { show_media_analysis } from './media_analysis.js';
import { show_user_analysis } from './user_analysis.js';
import { show_tweet_analysis } from './tweet_analysis.js';
import { show_network_metric_analysis } from './network_metric_analysis.js';
import { show_speech_analysis } from './speech_analysis.js';
import { show_topic_analysis } from './topic_analysis.js';

getSessionData()
.then(sessionData => {
    sessionData = sessionData.analysis_result

    // 1. Motto Analysis
    show_motto_analysis(sessionData)

    // 2. Media analysis
    show_media_analysis(sessionData)

    // 3. User analysis
    show_user_analysis(sessionData)

    // 4. Tweet analysis
    show_tweet_analysis(sessionData)

    // 5. Network metric analysis
    show_network_metric_analysis(sessionData)

    // 6. Speech analysis
    show_speech_analysis(sessionData)

    // // 7. Topic analysis
    // show_topic_analysis(sessionData)

    return sessionData
})
.catch(error => {
    console.log('Error:', error);
    return undefined
})
