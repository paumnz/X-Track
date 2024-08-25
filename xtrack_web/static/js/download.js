document.getElementById('download-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const start_date_input = document.getElementById('start-date').value;
    const trending_topics_input = document.getElementById('trending-topics').value;
    const city_input = document.getElementById('city').value;
    const days_input = document.getElementById('days').value;
    const campaign_input = document.getElementById('campaign').value;

    document.getElementById('loading-spinner').style.display = 'flex';

    fetch('/ingest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ start_date: start_date_input, trending_topics: trending_topics_input, city: city_input, days: days_input, campaign: campaign_input })
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            document.getElementById('loading-spinner').style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('loading-spinner').style.display = 'none';
    });
});
