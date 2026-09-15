document.addEventListener('DOMContentLoaded', () => {
    // Only run if radar chart canvas exists
    const ctx = document.getElementById('radarChart');
    if (!ctx) return;

    if (typeof currentPlayer === 'undefined') return;

    // Define chart config
    const labels = ['Pace', 'Shooting', 'Passing', 'Dribbling', 'Defending', 'Physical'];
    const p1Stats = [
        currentPlayer.stats.Pace,
        currentPlayer.stats.Shooting,
        currentPlayer.stats.Passing,
        currentPlayer.stats.Dribbling,
        currentPlayer.stats.Defending,
        currentPlayer.stats.Physical
    ];

    const data = {
        labels: labels,
        datasets: [{
            label: currentPlayer.name,
            data: p1Stats,
            fill: true,
            backgroundColor: 'rgba(37, 99, 235, 0.2)', // vibrant blue transparent
            borderColor: 'rgb(37, 99, 235)',
            pointBackgroundColor: 'rgb(37, 99, 235)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgb(37, 99, 235)'
        }]
    };

    const config = {
        type: 'radar',
        data: data,
        options: {
            elements: {
                line: {
                    borderWidth: 3
                }
            },
            scales: {
                r: {
                    angleLines: {
                        display: true,
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: '#cbd5e1'
                    },
                    pointLabels: {
                        color: '#334155',
                        font: {
                            size: 13,
                            weight: 'bold'
                        }
                    },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    ticks: {
                        stepSize: 20,
                        backdropColor: 'transparent',
                        color: '#64748b'
                    }
                }
            },
            maintainAspectRatio: false
        },
    };

    let radarChart = new Chart(ctx, config);

    // 1v1 Comparison Logic
    const opponentSelect = document.getElementById('opponentSelect');
    const compareBtn = document.getElementById('compareBtn');
    const clearBtn = document.getElementById('clearBtn');
    const comparisonDetails = document.getElementById('comparisonDetails');

    const oppImg = document.getElementById('oppImg');
    const oppName = document.getElementById('oppName');
    const oppCountry = document.getElementById('oppCountry');

    compareBtn.addEventListener('click', () => {
        const oppId = opponentSelect.value;
        if (!oppId) {
            alert('Please select an opponent to compare.');
            return;
        }

        // Fetch opponent data from API
        fetch(`/api/player/${oppId}`)
            .then(res => res.json())
            .then(oppData => {
                if(oppData.error) {
                    alert('Error loading opponent data');
                    return;
                }

                // Update UI
                oppImg.src = oppData.photo_url;
                oppName.textContent = oppData.name;
                oppCountry.textContent = oppData.country;
                comparisonDetails.classList.remove('hidden');
                comparisonDetails.classList.add('grid');
                clearBtn.classList.remove('hidden');
                compareBtn.classList.add('hidden');
                opponentSelect.disabled = true;

                // Update Chart
                const oppStats = [
                    oppData.stats.Pace,
                    oppData.stats.Shooting,
                    oppData.stats.Passing,
                    oppData.stats.Dribbling,
                    oppData.stats.Defending,
                    oppData.stats.Physical
                ];

                const oppDataset = {
                    label: oppData.name,
                    data: oppStats,
                    fill: true,
                    backgroundColor: 'rgba(239, 68, 68, 0.2)', // red-500 transparent
                    borderColor: 'rgb(239, 68, 68)',
                    pointBackgroundColor: 'rgb(239, 68, 68)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(239, 68, 68)'
                };

                // Add to chart if not already there
                if(radarChart.data.datasets.length === 1) {
                    radarChart.data.datasets.push(oppDataset);
                    radarChart.update();
                }
            })
            .catch(err => {
                console.error(err);
                alert('Error connecting to the server');
            });
    });

    clearBtn.addEventListener('click', () => {
        // Reset Chart
        if(radarChart.data.datasets.length > 1) {
            radarChart.data.datasets.pop();
            radarChart.update();
        }

        // Reset UI
        comparisonDetails.classList.remove('grid');
        comparisonDetails.classList.add('hidden');
        clearBtn.classList.add('hidden');
        compareBtn.classList.remove('hidden');
        opponentSelect.disabled = false;
        opponentSelect.value = "";
    });
});
