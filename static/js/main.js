/**
 * ========================================================================
 * EDUSHIELD: AI-POWERED STUDENT RETENTION ANALYTICS PLATFORM
 * Custom JavaScript & Interactive Behaviors (Grand Light/Dark Theme)
 * ========================================================================
 */

// Theme Toggle Globals
const themeKey = 'edushield-theme';
function applyTheme(theme) {
    const icon = document.getElementById('theme-toggle-icon');
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        if (icon) {
            icon.className = 'fas fa-sun';
            icon.style.color = '#eab308';
        }
    } else {
        document.body.classList.remove('dark-theme');
        if (icon) {
            icon.className = 'fas fa-moon';
            icon.style.color = '';
        }
    }
}

// Immediate theme execution to prevent page flashes
const currentTheme = localStorage.getItem(themeKey) || 'light';
applyTheme(currentTheme);

document.addEventListener('DOMContentLoaded', function () {
    // Initialize top navigation mobile toggle
    initMobileTopNav();
    
    // Initialize theme button click listener
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) {
        themeBtn.addEventListener('click', function() {
            const activeTheme = document.body.classList.contains('dark-theme') ? 'light' : 'dark';
            localStorage.setItem(themeKey, activeTheme);
            applyTheme(activeTheme);
        });
    }

    // Check which page is currently active and render corresponding components
    const path = window.location.pathname;
    
    if (path.includes('/dashboard')) {
        renderDashboardCharts();
    } else if (path.includes('/dataset')) {
        renderDatasetCharts();
    } else if (path.includes('/model-comparison') || path.includes('/model-performance')) {
        renderModelComparisonCharts();
    } else if (path.includes('/prediction')) {
        initPredictionForm();
    }
});

/**
 * Mobile Top Navbar Toggle Logic
 */
function initMobileTopNav() {
    const toggleBtn = document.getElementById('nav-toggle-btn');
    const menuList = document.getElementById('nav-menu-list');

    if (toggleBtn && menuList) {
        toggleBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            menuList.classList.toggle('open');
            const isOpen = menuList.classList.contains('open');
            toggleBtn.innerHTML = isOpen ? '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function (e) {
            if (menuList.classList.contains('open') && !menuList.contains(e.target) && e.target !== toggleBtn) {
                menuList.classList.remove('open');
                toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
            }
        });
    }
}

/**
 * Renders Interactive Plotly Charts on the Dashboard (Light Theme layout)
 */
function renderDashboardCharts() {
    const defaultLayout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Inter, sans-serif', color: '#64748b' },
        margin: { l: 45, r: 20, t: 40, b: 50 },
        height: 330, // Fixed height to prevent overlapping
        hovermode: 'closest',
        xaxis: { gridcolor: 'rgba(0, 0, 0, 0.05)', zerolinecolor: 'rgba(0, 0, 0, 0.05)' },
        yaxis: { gridcolor: 'rgba(0, 0, 0, 0.05)', zerolinecolor: 'rgba(0, 0, 0, 0.05)' }
    };

    // 1. Dropout / Academic Success Distribution (Pie Chart)
    const pieDiv = document.getElementById('dropout-dist-chart');
    if (pieDiv) {
        const data = [{
            values: [1421, 2209, 794],
            labels: ['Dropout', 'Graduate', 'Enrolled'],
            type: 'pie',
            hole: 0.5,
            marker: {
                colors: ['#dc2626', '#10b981', '#2563eb']
            },
            textinfo: 'label+percent',
            insidetextorientation: 'radial',
            textfont: { color: '#ffffff' }
        }];
        const layout = {
            ...defaultLayout,
            margin: { l: 20, r: 20, t: 20, b: 20 },
            showlegend: true,
            legend: { orientation: 'h', x: 0, y: -0.15, font: { color: '#64748b' } }
        };
        pieDiv.innerHTML = ''; // Clear placeholder loader spinner & text
        Plotly.newPlot(pieDiv, data, layout, { responsive: true, displayModeBar: false });
    }

    // 2. Department-wise Dropout Rate (Bar Chart)
    const deptDiv = document.getElementById('dept-dropout-chart');
    if (deptDiv) {
        const courses = ['Nursing', 'Management', 'Informatics Eng', 'Social Service', 'Design', 'Agriculture', 'Biofuels'];
        const dropoutRates = [18.2, 41.5, 52.8, 22.4, 31.0, 38.6, 68.2];
        const data = [{
            x: dropoutRates,
            y: courses,
            type: 'bar',
            orientation: 'h',
            marker: {
                color: dropoutRates.map(r => r > 45 ? '#dc2626' : (r > 30 ? '#d97706' : '#2563eb')),
                opacity: 0.85
            }
        }];
        const layout = {
            ...defaultLayout,
            margin: { l: 110, r: 20, t: 20, b: 40 },
            xaxis: { ...defaultLayout.xaxis, title: 'Dropout Percentage (%)' },
            yaxis: { automargin: true }
        };
        deptDiv.innerHTML = ''; // Clear placeholder loader spinner & text
        Plotly.newPlot(deptDiv, data, layout, { responsive: true, displayModeBar: false });
    }

    // 3. Scholarship Holder vs Retention (Grouped Bar Chart)
    const scholarDiv = document.getElementById('scholarship-chart');
    if (scholarDiv) {
        const data = [
            {
                x: ['Scholarship Holders', 'Non-Holders'],
                y: [86.5, 55.2],
                name: 'Graduate / Enrolled',
                type: 'bar',
                marker: { color: '#10b981' }
            },
            {
                x: ['Scholarship Holders', 'Non-Holders'],
                y: [13.5, 44.8],
                name: 'Dropout',
                type: 'bar',
                marker: { color: '#dc2626' }
            }
        ];
        const layout = {
            ...defaultLayout,
            barmode: 'group',
            yaxis: { ...defaultLayout.yaxis, title: 'Percentage (%)' },
            legend: { orientation: 'h', x: 0, y: -0.2, font: { color: '#64748b' } }
        };
        scholarDiv.innerHTML = ''; // Clear placeholder loader spinner & text
        Plotly.newPlot(scholarDiv, data, layout, { responsive: true, displayModeBar: false });
    }

    // 4. Semester Performance (Scatter Plot)
    const perfDiv = document.getElementById('semester-perf-chart');
    if (perfDiv) {
        // Discrete integer values for curricular credits x-axis to prevent fractional float ticks
        const graduatesX = Array.from({length: 40}, () => Math.floor(Math.random() * 9) + 4); 
        const graduatesY = Array.from({length: 40}, () => Math.round((Math.random() * 6 + 12) * 10) / 10);
        const dropoutsX = Array.from({length: 40}, () => Math.floor(Math.random() * 5));
        const dropoutsY = Array.from({length: 40}, () => Math.round((Math.random() * 8 + 4) * 10) / 10);

        const data = [
            {
                x: graduatesX,
                y: graduatesY,
                mode: 'markers',
                type: 'scatter',
                name: 'Graduates',
                marker: { color: '#10b981', size: 9, opacity: 0.7 }
            },
            {
                x: dropoutsX,
                y: dropoutsY,
                mode: 'markers',
                type: 'scatter',
                name: 'Dropouts',
                marker: { color: '#dc2626', size: 9, opacity: 0.7 }
            }
        ];
        const layout = {
            ...defaultLayout,
            xaxis: { ...defaultLayout.xaxis, title: '1st Sem Approved Credits', dtick: 1 }, 
            yaxis: { ...defaultLayout.yaxis, title: '1st Sem Grade (0-20)' },
            legend: { orientation: 'h', x: 0, y: -0.2, font: { color: '#64748b' } }
        };
        perfDiv.innerHTML = ''; // Clear placeholder loader spinner & text
        Plotly.newPlot(perfDiv, data, layout, { responsive: true, displayModeBar: false });
    }
}

/**
 * Renders Charts on the Dataset Overview Page (Light Theme layout)
 */
function renderDatasetCharts() {
    const defaultLayout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Inter, sans-serif', color: '#64748b' },
        margin: { l: 45, r: 20, t: 40, b: 50 },
        height: 330, // Fixed height to prevent overlapping
        xaxis: { gridcolor: 'rgba(0, 0, 0, 0.05)', zerolinecolor: 'rgba(0, 0, 0, 0.05)' },
        yaxis: { gridcolor: 'rgba(0, 0, 0, 0.05)', zerolinecolor: 'rgba(0, 0, 0, 0.05)' }
    };

    // 1. Age at Enrollment Distribution (Histogram)
    const ageDiv = document.getElementById('age-dist-chart');
    if (ageDiv) {
        const ages = [];
        for (let i = 0; i < 500; i++) {
            const rand = Math.random();
            if (rand < 0.6) {
                ages.push(Math.floor(Math.random() * 5) + 18);
            } else if (rand < 0.85) {
                ages.push(Math.floor(Math.random() * 7) + 23);
            } else {
                ages.push(Math.floor(Math.random() * 20) + 30);
            }
        }
        const data = [{
            x: ages,
            type: 'histogram',
            marker: { color: '#2563eb', opacity: 0.7 }
        }];
        const layout = {
            ...defaultLayout,
            xaxis: { ...defaultLayout.xaxis, title: 'Age at Enrollment' },
            yaxis: { ...defaultLayout.yaxis, title: 'Number of Students' }
        };
        ageDiv.innerHTML = ''; // Clear placeholder loader spinner & text
        Plotly.newPlot(ageDiv, data, layout, { responsive: true, displayModeBar: false });
    }

    // 2. Financial Status Stacked Bar Chart
    const financialDiv = document.getElementById('financial-status-chart');
    if (financialDiv) {
        const data = [
            {
                x: ['Tuition Up to Date', 'Tuition Overdue'],
                y: [88.2, 11.8],
                name: 'Not Debtor',
                type: 'bar',
                marker: { color: '#2563eb' }
            },
            {
                x: ['Tuition Up to Date', 'Tuition Overdue'],
                y: [4.5, 95.5],
                name: 'Debtor',
                type: 'bar',
                marker: { color: '#dc2626' }
            }
        ];
        const layout = {
            ...defaultLayout,
            barmode: 'stack',
            yaxis: { ...defaultLayout.yaxis, title: 'Percentage (%)' },
            legend: { orientation: 'h', x: 0, y: -0.2, font: { color: '#64748b' } }
        };
        financialDiv.innerHTML = ''; // Clear placeholder loader spinner & text
        Plotly.newPlot(financialDiv, data, layout, { responsive: true, displayModeBar: false });
    }
}

/**
 * Renders Performance Charts on the Model Comparison Page (Light Theme layout)
 */
function renderModelComparisonCharts() {
    const modelDiv = document.getElementById('models-comparison-bar-chart');
    if (modelDiv) {
        let models = ['XGBoost Classifier', 'Random Forest Classifier', 'Logistic Regression', 'Gradient Boosting Classifier', 'Support Vector Machine (SVM)', 'K-Nearest Neighbors (KNN)', 'Decision Tree Classifier'];
        let accuracies = [88.25, 88.25, 88.02, 87.23, 87.57, 84.07, 79.44];
        let f1Scores = [80.74, 80.08, 79.69, 78.72, 77.91, 70.81, 69.26];

        if (window.modelBenchmarkData && window.modelBenchmarkData.length > 0) {
            models = window.modelBenchmarkData.map(m => m.name);
            accuracies = window.modelBenchmarkData.map(m => m.accuracy);
            f1Scores = window.modelBenchmarkData.map(m => m.f1_score);
        }

        const data = [
            {
                x: models,
                y: accuracies,
                name: 'Accuracy',
                type: 'bar',
                marker: { color: '#2563eb', opacity: 0.85 }
            },
            {
                x: models,
                y: f1Scores,
                name: 'F1 Score',
                type: 'bar',
                marker: { color: '#7c3aed', opacity: 0.85 }
            }
        ];

        const layout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { family: 'Inter, sans-serif', color: '#64748b' },
            height: 350, // Fixed height to prevent overlapping
            margin: { l: 45, r: 20, t: 40, b: 60 },
            barmode: 'group',
            xaxis: { gridcolor: 'rgba(0, 0, 0, 0.04)' },
            yaxis: { title: 'Score (%)', range: [50, 100], gridcolor: 'rgba(0, 0, 0, 0.04)' },
            legend: { orientation: 'h', x: 0, y: -0.2, font: { color: '#64748b' } }
        };

        modelDiv.innerHTML = ''; // Clear placeholder loader spinner & text
        Plotly.newPlot(modelDiv, data, layout, { responsive: true, displayModeBar: false });
    }
}

/**
 * Handles Prediction Form Submissions via AJAX
 */
function initPredictionForm() {
    const form = document.getElementById('prediction-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        // Get submit button and show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Analyzing Academic Profile...';

        // Prepare form data
        const formData = new FormData(form);

        // Perform AJAX request
        fetch('/predict', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Prediction API failed');
            return response.json();
        })
        .then(result => {
            displayPredictionResults(result);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while calculating the risk assessment. Please check details and try again.');
        })
        .finally(() => {
            // Restore button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        });
    });
}

/**
 * Dynamically updates the Prediction results panel in the DOM (Light Theme layout)
 */
function displayPredictionResults(result) {
    const resultsPanel = document.getElementById('prediction-results-panel');
    const helpCard = document.getElementById('form-help-card');
    
    if (!resultsPanel) return;

    // Show the results section, hide default instructions
    if (helpCard) helpCard.classList.add('d-none');
    resultsPanel.classList.remove('d-none');
    resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Update risk banner
    const banner = document.getElementById('res-risk-banner');
    banner.className = 'risk-alert-banner'; // clear previous risk-classes
    
    let bannerIcon = '';
    if (result.risk_level === 'High') {
        banner.classList.add('risk-high');
        bannerIcon = '<i class="fas fa-exclamation-triangle"></i>';
    } else if (result.risk_level === 'Medium') {
        banner.classList.add('risk-medium');
        bannerIcon = '<i class="fas fa-exclamation-circle"></i>';
    } else {
        banner.classList.add('risk-low');
        bannerIcon = '<i class="fas fa-check-circle"></i>';
    }
    banner.innerHTML = `${bannerIcon} ${result.risk_level} Risk Level Assessment`;

    // Update labels and values
    document.getElementById('res-classification').innerText = result.prediction;
    document.getElementById('res-classification').className = 
        result.prediction === 'At Risk' ? 'text-danger fw-bold' : 'text-success fw-bold';

    document.getElementById('res-probability').innerText = `${Math.round(result.probability * 100)}%`;
    document.getElementById('res-confidence').innerText = `${result.confidence}%`;

    // Render recommendations
    const recsList = document.getElementById('res-recommendations');
    recsList.innerHTML = '';
    result.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.innerHTML = `<i class="fas fa-chevron-right text-secondary"></i> ${rec}`;
        recsList.appendChild(li);
    });

    // Update PDF Report Link
    const pdfBtn = document.getElementById('res-pdf-btn');
    if (pdfBtn) {
        if (result.id) {
            pdfBtn.href = '/prediction/pdf/' + result.id;
            pdfBtn.classList.remove('d-none');
        } else {
            pdfBtn.classList.add('d-none');
        }
    }

    // Draw the light mode gauge
    const gaugeContainer = document.getElementById('risk-gauge-container');
    if (gaugeContainer) {
        gaugeContainer.innerHTML = ''; // Clear previous
        
        const gaugeData = [{
            domain: { x: [0, 1], y: [0, 1] },
            value: result.probability * 100,
            title: { text: "Dropout Probability", font: { size: 12, color: '#64748b' } },
            type: "indicator",
            mode: "gauge+number",
            number: { font: { color: '#0f172a' } },
            gauge: {
                axis: { range: [0, 100], tickcolor: '#64748b', font: { color: '#64748b' } },
                bar: { color: result.risk_level === 'High' ? '#dc2626' : (result.risk_level === 'Medium' ? '#d97706' : '#10b981') },
                bgcolor: "rgba(0,0,0,0.03)",
                borderwidth: 1,
                bordercolor: "rgba(0,0,0,0.08)",
                steps: [
                    { range: [0, 35], color: "rgba(16, 185, 129, 0.05)" },
                    { range: [35, 60], color: "rgba(217, 119, 6, 0.05)" },
                    { range: [60, 100], color: "rgba(220, 38, 38, 0.05)" }
                ]
            }
        }];

        const gaugeLayout = {
            width: 250,
            height: 170,
            margin: { t: 30, b: 10, l: 30, r: 30 },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            font: { family: "Inter, sans-serif" }
        };

        Plotly.newPlot(gaugeContainer, gaugeData, gaugeLayout, { displayModeBar: false });
    }
}
