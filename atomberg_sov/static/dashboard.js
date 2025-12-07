/* =====================================================
   ATOMBERG SoV DASHBOARD - JAVASCRIPT
   ===================================================== */

let charts = {};
let currentAnalysisData = null;

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');
    loadDemoData();
    setupEventListeners();
});

/**
 * Setup event listeners for buttons
 */
function setupEventListeners() {
    const loadDefaultBtn = document.getElementById('loadDefault');
    const runBtn = document.getElementById('runAnalysis');

    if (loadDefaultBtn) loadDefaultBtn.addEventListener('click', loadDemoData);
    if (runBtn) runBtn.addEventListener('click', runAnalysis);
}

/**
 * Load demo data
 */
async function loadDemoData() {
    try {
        const response = await fetch('/api/demo');
        const data = await response.json();
        
        if (data) {
            currentAnalysisData = data;
            updateDashboard(currentAnalysisData);
            console.log('✅ Demo data loaded successfully!');
        }
    } catch (error) {
        console.error('Error loading demo data:', error);
    }
}

/**
 * Run analysis - triggers backend analysis
 */
async function runAnalysis() {
    const button = document.getElementById('runAnalysis');
    button.disabled = true;
    button.textContent = 'Running...';
    
    try {
        // Get form values
        const brand = document.getElementById('primaryBrand')?.value || 'atomberg';
        const brandKeywords = document.getElementById('brandKeywords')?.value || 'atomberg';
        const competitors = document.getElementById('competitors')?.value || 'havells';
        const searchKeywords = document.getElementById('searchKeywords')?.value || 'smart fan';

        const requestData = {
            brand_keywords: {
                [brand]: brandKeywords.split(',').map(k => k.trim())
            },
            search_keywords: searchKeywords.split(',').map(k => k.trim()),
            competitors: competitors.split(',').map(c => c.trim())
        };

        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        currentAnalysisData = data;
        updateDashboard(currentAnalysisData);
        console.log('✅ Analysis completed successfully!');
    } catch (error) {
        console.error('Analysis error:', error);
        alert('Error running analysis: ' + error.message);
    } finally {
        button.disabled = false;
        button.textContent = 'Run Analysis';
    }
}

/**
 * Update entire dashboard with new data
 */
function updateDashboard(data) {
    if (!data) return;

    try {
        updateMetrics(data);
        updateCharts(data);
        updateTables(data);
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

/**
 * Update metric cards
 */
function updateMetrics(data) {
    try {
        const insights = data.aggregate_insights || data;
        
        // Average SoV
        const sovCard = document.querySelector('[data-metric="sov"]');
        if (sovCard) {
            const value = insights.average_sov || 35;
            const valueElem = sovCard.querySelector('.metric-value');
            if (valueElem) {
                valueElem.innerHTML = `${value.toFixed(1)}<span class="metric-unit">%</span>`;
            }
        }

        // Keywords Analyzed
        const keywordsCard = document.querySelector('[data-metric="keywords"]');
        if (keywordsCard) {
            const value = insights.keywords_analyzed || 5;
            const valueElem = keywordsCard.querySelector('.metric-value');
            if (valueElem) {
                valueElem.textContent = value;
            }
        }

        // Top SoV Keyword
        const topCard = document.querySelector('[data-metric="top"]');
        if (topCard) {
            const keywords = insights.top_keywords || ['smart fan'];
            const valueElem = topCard.querySelector('.metric-value');
            if (valueElem) {
                valueElem.textContent = keywords[0] || 'N/A';
            }
        }

        // Competitors
        const compCard = document.querySelector('[data-metric="competitors"]');
        if (compCard) {
            const count = Object.keys(data.keyword_analyses || {}).length > 0 ? 5 : 4;
            const valueElem = compCard.querySelector('.metric-value');
            if (valueElem) {
                valueElem.textContent = count;
            }
        }
        
        console.log('✅ Metrics updated successfully!');
    } catch (error) {
        console.error('Error updating metrics:', error);
    }
}

/**
 * Update all charts
 */
function updateCharts(data) {
    if (!data) return;

    try {
        updateSoVChart(data);
        updateSentimentChart(data);
        updateCompetitorChart(data);
    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

/**
 * Update SoV Distribution Chart (Doughnut)
 */
function updateSoVChart(data) {
    const ctx = document.getElementById('sovChart');
    if (!ctx) return;

    try {
        const keywordAnalyses = data.keyword_analyses || {};
        const keywords = Object.keys(keywordAnalyses).slice(0, 5);
        const sovValues = keywords.map(kw => {
            return keywordAnalyses[kw]?.sov_analysis?.share_of_voice || 0;
        });

        if (charts.sovChart) {
            charts.sovChart.data.labels = keywords;
            charts.sovChart.data.datasets[0].data = sovValues;
            charts.sovChart.update();
        } else {
            charts.sovChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: keywords,
                    datasets: [{
                        data: sovValues,
                        backgroundColor: ['#2563eb', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        }
    } catch (error) {
        console.error('Error updating SoV chart:', error);
    }
}

/**
 * Update Sentiment Chart (Bar)
 */
function updateSentimentChart(data) {
    const ctx = document.getElementById('sentimentChart');
    if (!ctx) return;

    try {
        const keywordAnalyses = data.keyword_analyses || {};
        const keywords = Object.keys(keywordAnalyses).slice(0, 5);
        
        const positive = keywords.map(kw => keywordAnalyses[kw]?.sentiment_analysis?.positive || 50);
        const neutral = keywords.map(kw => keywordAnalyses[kw]?.sentiment_analysis?.neutral || 30);
        const negative = keywords.map(kw => keywordAnalyses[kw]?.sentiment_analysis?.negative || 20);

        if (charts.sentimentChart) {
            charts.sentimentChart.data.labels = keywords;
            charts.sentimentChart.data.datasets[0].data = positive;
            charts.sentimentChart.data.datasets[1].data = neutral;
            charts.sentimentChart.data.datasets[2].data = negative;
            charts.sentimentChart.update();
        } else {
            charts.sentimentChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: keywords,
                    datasets: [
                        { label: 'Positive', data: positive, backgroundColor: '#10b981' },
                        { label: 'Neutral', data: neutral, backgroundColor: '#64748b' },
                        { label: 'Negative', data: negative, backgroundColor: '#ef4444' }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: { x: { stacked: false }, y: { stacked: false } },
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        }
    } catch (error) {
        console.error('Error updating sentiment chart:', error);
    }
}

/**
 * Update Competitor Chart (Horizontal Bar)
 */
function updateCompetitorChart(data) {
    const ctx = document.getElementById('competitorChart');
    if (!ctx) return;

    try {
        const keywordAnalyses = data.keyword_analyses || {};
        const keywords = Object.keys(keywordAnalyses).slice(0, 5);
        const sovValues = keywords.map(kw => keywordAnalyses[kw]?.sov_analysis?.share_of_voice || 0);

        if (charts.competitorChart) {
            charts.competitorChart.data.labels = keywords;
            charts.competitorChart.data.datasets[0].data = sovValues;
            charts.competitorChart.update();
        } else {
            charts.competitorChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: keywords,
                    datasets: [{
                        label: 'SoV %',
                        data: sovValues,
                        backgroundColor: '#2563eb'
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: { x: { max: 100 } },
                    plugins: { legend: { display: false } }
                }
            });
        }
    } catch (error) {
        console.error('Error updating competitor chart:', error);
    }
}

/**
 * Update Tables
 */
function updateTables(data) {
    try {
        const tbody = document.getElementById('resultsTable');
        if (!tbody) return;

        const keywordAnalyses = data.keyword_analyses || {};
        let html = '';

        Object.entries(keywordAnalyses).forEach(([keyword, analysis]) => {
            const sov = analysis.sov_analysis?.share_of_voice || 0;
            const rank = analysis.sov_analysis?.rank || '-';
            const mentions = analysis.sov_analysis?.total_mentions || 0;
            const sentiment = analysis.sentiment_analysis || {};
            const positive = sentiment.positive || 0;
            const neutral = sentiment.neutral || 0;
            const negative = sentiment.negative || 0;

            html += `
                <tr>
                    <td>${keyword}</td>
                    <td>${sov.toFixed(1)}%</td>
                    <td>${rank}</td>
                    <td>${mentions}</td>
                    <td>+${positive}% =${neutral}% -${negative}%</td>
                </tr>
            `;
        });

        tbody.innerHTML = html || '<tr><td colspan="5">No data available</td></tr>';
    } catch (error) {
        console.error('Error updating tables:', error);
    }
}

/**
 * Download Report in requested format
 */
async function downloadReport(format) {
    if (!currentAnalysisData) {
        alert('Please run analysis first to generate report');
        return;
    }

    try {
        const response = await fetch('/api/generate-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                analysis_data: currentAnalysisData,
                format: format
            })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const reportData = await response.json();
        const filename = reportData.filename || `atomberg_report.${format}`;
        const content = reportData.content;

        // Create blob and download
        let blob, mimeType;
        
        if (format === 'html') {
            blob = new Blob([content], { type: 'text/html' });
        } else if (format === 'json') {
            blob = new Blob([JSON.stringify(content, null, 2)], { type: 'application/json' });
        } else if (format === 'csv') {
            blob = new Blob([content], { type: 'text/csv' });
        } else if (format === 'txt') {
            blob = new Blob([content], { type: 'text/plain' });
        }

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        console.log(`✅ Report downloaded: ${filename}`);
        
        // Show preview for HTML
        if (format === 'html') {
            const previewContainer = document.getElementById('reportContainer');
            const previewDiv = document.getElementById('reportPreview');
            previewDiv.innerHTML = content;
            previewContainer.style.display = 'block';
            previewDiv.scrollIntoView({ behavior: 'smooth' });
        }

    } catch (error) {
        console.error('Error downloading report:', error);
        alert('Error generating report: ' + error.message);
    }
}

/**
 * Refresh dashboard data
 */
function refreshDashboard() {
    console.log('Refreshing dashboard...');
    loadDemoData();
}

/**
 * Load default analysis (alias for loadDemoData)
 */
function loadDefaultAnalysis() {
    console.log('Loading default analysis...');
    loadDemoData();
}

console.log('Dashboard JavaScript loaded successfully!');
