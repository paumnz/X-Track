document.getElementById('analysis-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const input1 = document.getElementById('input1').value;
    const input2 = document.getElementById('input2').value;

    document.getElementById('loading-spinner').style.display = 'flex';

    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ campaigns: input1, hashtags: input2 })
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
