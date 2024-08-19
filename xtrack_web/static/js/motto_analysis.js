import { create_bar_plot } from './utils.js';
import { destroyChart } from './utils.js';

export function show_motto_analysis(sessionData) {

    // Retrieving canvas and visualization elements
    const sentimentSelect = document.getElementById('sentiment-select');
    const mottoAllCanvas = document.getElementById('cv_motto_all');
    const mottoNegativeCanvas = document.getElementById('cv_motto_negative');
    const mottoPositiveCanvas = document.getElementById('cv_motto_positive');

    // Plotting the information
    sentimentSelect.addEventListener('change', function() {
        const selectedValue = this.value;

        // Hide all canvases initially
        mottoAllCanvas.style.display = 'none';
        mottoNegativeCanvas.style.display = 'none';
        mottoPositiveCanvas.style.display = 'none';

        // Show the selected canvas
        if (selectedValue === 'all') {
            destroyChart('cv_motto_all')
            mottoAllCanvas.style.display = 'block';
            create_bar_plot(sessionData.motto_analysis['all'], mottoAllCanvas)
        } else if (selectedValue === 'positive') {
            destroyChart('cv_motto_positive')
            mottoPositiveCanvas.style.display = 'block';
            create_bar_plot(sessionData.motto_analysis['positive'], mottoPositiveCanvas)
        } else if (selectedValue === 'negative') {
            destroyChart('cv_motto_negative')
            mottoNegativeCanvas.style.display = 'block';
            create_bar_plot(sessionData.motto_analysis['negative'], mottoNegativeCanvas)
        }
    });

    // Set initial visibility based on default selection
    sentimentSelect.dispatchEvent(new Event('change'));
}