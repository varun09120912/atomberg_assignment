/**
 * ATOMBERG SoV AGENT - User Input Handler
 * Manages user search, history, and export functionality
 */

// =====================================================
// INITIALIZATION
// =====================================================

let searchHistory = [];
let currentAnalysisData = null;

document.addEventListener('DOMContentLoaded', function() {
    loadSearchHistory();
    loadInitialData();
});

// =====================================================
// SEARCH FUNCTIONALITY
// =====================================================

/**
 * Perform search based on user input
 */
async function performSearch() {
    const keywordsInput = document.getElementById('keywordsInput').value.trim();
    const resultsCount = parseInt(document.getElementById('resultsCount').value) || 10;
    const analysisType = document.getElementById('analysisType').value;
    
    // Validate input
    if (!keywordsInput) {
        showStatus('❌ Please enter at least one keyword', 'error');
        return;
    }
    
    // Parse keywords
    const keywords = keywordsInput
        .split(',')
        .map(k => k.trim())
        .filter(k => k.length > 0);
    
    if (keywords.length === 0) {
        showStatus('❌ Invalid keyword format', 'error');
        return;
    }
    
    // Show loading state
    showLoadingState(true);
    showStatus('🔍 Analyzing ' + keywords.length + ' keyword(s)...', 'loading');
    
    try {
        // Call backend API
        const response = await axios.post('/api/user-search', {
            keywords: keywords,
            num_results: resultsCount,
            analysis_type: analysisType
        }, {
            timeout: 300000 // 5 minute timeout
        });
        
        if (response.data && response.data.success) {
            currentAnalysisData = response.data.data;
            
            // Add to history
            addToHistory({
                timestamp: new Date().toLocaleString(),
                keywords: keywords,
                analysis_type: analysisType,
                results_count: resultsCount
            });
            
            // Update dashboard
            updateDashboard(response.data.data);
            
            // Enable export buttons
            enableExportButtons();
            
            showStatus(`✅ Analysis complete! Analyzed ${keywords.length} keyword(s)`, 'success');
        } else {
            showStatus('❌ Analysis failed: ' + (response.data.message || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Search error:', error);
        if (error.response?.data?.message) {
            showStatus('❌ Error: ' + error.response.data.message, 'error');
        } else if (error.message === 'timeout of 300000ms exceeded') {
            showStatus('❌ Analysis timed out. Please try fewer keywords or reduce results count.', 'error');
        } else {
            showStatus('❌ Error: ' + error.message, 'error');
        }
    } finally {
        showLoadingState(false);
    }
}

/**
 * Clear the search form
 */
function clearForm() {
    document.getElementById('keywordsInput').value = 'smart fan, smart ceiling fan, WiFi controlled fan';
    document.getElementById('resultsCount').value = 10;
    document.getElementById('analysisType').value = 'full';
    showStatus('✨ Form cleared', 'info');
}

/**
 * Show status message with color coding
 */
function showStatus(message, type = 'info') {
    const statusElement = document.getElementById('analysisStatus');
    if (!statusElement) return;
    
    statusElement.textContent = message;
    statusElement.className = 'status-text status-' + type;
    
    // Auto-clear after 5 seconds for non-loading messages
    if (type !== 'loading') {
        setTimeout(() => {
            if (statusElement.textContent === message) {
                statusElement.textContent = '';
            }
        }, 5000);
    }
}

/**
 * Show/hide loading state
 */
function showLoadingState(isLoading) {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (loadingOverlay) {
        loadingOverlay.style.display = isLoading ? 'flex' : 'none';
    }
    
    if (analyzeBtn) {
        analyzeBtn.disabled = isLoading;
        analyzeBtn.textContent = isLoading ? 
            '⏳ Analyzing...' : 
            '🔎 Search & Analyze';
    }
}

/**
 * Enable export buttons after successful analysis
 */
function enableExportButtons() {
    const exportButtons = document.querySelectorAll('#exportJsonBtn, #exportCsvBtn, #printBtn');
    exportButtons.forEach(btn => btn.disabled = false);
}

// =====================================================
// SEARCH HISTORY MANAGEMENT
// =====================================================

/**
 * Add search to history
 */
function addToHistory(searchEntry) {
    // Add to beginning of array (most recent first)
    searchHistory.unshift(searchEntry);
    
    // Keep only last 10 searches
    if (searchHistory.length > 10) {
        searchHistory = searchHistory.slice(0, 10);
    }
    
    saveSearchHistory();
}

/**
 * Save history to localStorage
 */
function saveSearchHistory() {
    try {
        localStorage.setItem('atomberg_search_history', JSON.stringify(searchHistory));
    } catch (error) {
        console.error('Failed to save history:', error);
    }
}

/**
 * Load history from localStorage
 */
function loadSearchHistory() {
    try {
        const saved = localStorage.getItem('atomberg_search_history');
        if (saved) {
            searchHistory = JSON.parse(saved);
        }
    } catch (error) {
        console.error('Failed to load history:', error);
        searchHistory = [];
    }
}

/**
 * Show search history modal
 */
function showHistory() {
    if (searchHistory.length === 0) {
        showStatus('📭 No search history yet', 'info');
        return;
    }
    
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'historyModal';
    
    let historyHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>📜 Search History</h2>
                <button class="modal-close" onclick="closeHistory()">✕</button>
            </div>
            <div class="modal-body">
                <div class="history-list">
    `;
    
    searchHistory.forEach((entry, index) => {
        const keywordsStr = entry.keywords.join(', ');
        historyHTML += `
            <div class="history-item">
                <div class="history-info">
                    <div class="history-time">${entry.timestamp}</div>
                    <div class="history-keywords"><strong>Keywords:</strong> ${keywordsStr}</div>
                    <div class="history-meta">
                        <span class="history-type">${entry.analysis_type}</span>
                        <span class="history-count">${entry.results_count} results</span>
                    </div>
                </div>
                <button class="history-restore" onclick="restoreSearch(${index})" title="Restore this search">
                    ↻ Restore
                </button>
            </div>
        `;
    });
    
    historyHTML += `
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="clearHistory()">🗑️ Clear History</button>
                <button class="btn btn-secondary" onclick="closeHistory()">Close</button>
            </div>
        </div>
    `;
    
    modal.innerHTML = historyHTML;
    document.body.appendChild(modal);
    
    // Add modal styles if not already present
    if (!document.getElementById('modalStyles')) {
        const style = document.createElement('style');
        style.id = 'modalStyles';
        style.textContent = `
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                animation: fadeIn 0.3s ease;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            .modal-content {
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                display: flex;
                flex-direction: column;
                animation: slideUp 0.3s ease;
            }
            
            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            
            .modal-header {
                padding: 20px;
                border-bottom: 2px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-header h2 {
                margin: 0;
                font-size: 20px;
                color: #2d3748;
            }
            
            .modal-close {
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #718096;
                transition: color 0.2s;
            }
            
            .modal-close:hover {
                color: #2d3748;
            }
            
            .modal-body {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
            }
            
            .history-list {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            
            .history-item {
                background: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: all 0.2s;
            }
            
            .history-item:hover {
                background: #edf2f7;
                border-color: #cbd5e0;
            }
            
            .history-info {
                flex: 1;
            }
            
            .history-time {
                font-size: 12px;
                color: #718096;
                margin-bottom: 6px;
            }
            
            .history-keywords {
                font-size: 14px;
                color: #2d3748;
                margin-bottom: 6px;
                word-break: break-word;
            }
            
            .history-meta {
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
            }
            
            .history-type,
            .history-count {
                font-size: 12px;
                background: white;
                padding: 4px 8px;
                border-radius: 4px;
                color: #667eea;
                font-weight: 600;
            }
            
            .history-restore {
                background: #667eea;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 600;
                transition: all 0.2s;
                white-space: nowrap;
                margin-left: 12px;
            }
            
            .history-restore:hover {
                background: #764ba2;
                transform: translateY(-2px);
            }
            
            .modal-footer {
                padding: 15px 20px;
                border-top: 2px solid #e2e8f0;
                display: flex;
                gap: 10px;
                justify-content: flex-end;
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Close history modal
 */
function closeHistory() {
    const modal = document.getElementById('historyModal');
    if (modal) {
        modal.remove();
    }
}

/**
 * Restore previous search
 */
function restoreSearch(index) {
    if (index < 0 || index >= searchHistory.length) return;
    
    const entry = searchHistory[index];
    document.getElementById('keywordsInput').value = entry.keywords.join(', ');
    document.getElementById('resultsCount').value = entry.results_count;
    document.getElementById('analysisType').value = entry.analysis_type;
    
    closeHistory();
    showStatus('✨ Search restored. Click "Search & Analyze" to run.', 'info');
}

/**
 * Clear all search history
 */
function clearHistory() {
    if (confirm('Are you sure you want to clear all search history?')) {
        searchHistory = [];
        saveSearchHistory();
        closeHistory();
        showStatus('🗑️ Search history cleared', 'success');
    }
}

// =====================================================
// EXPORT FUNCTIONALITY
// =====================================================

/**
 * Export analysis as JSON
 */
function exportJSON() {
    if (!currentAnalysisData) {
        showStatus('❌ No analysis data to export. Run analysis first.', 'error');
        return;
    }
    
    try {
        showStatus('📄 Preparing JSON export...', 'loading');
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
        const filename = `atomberg_sov_analysis_${timestamp}.json`;
        
        // Create comprehensive JSON with metadata
        const exportData = {
            metadata: {
                generated_at: new Date().toISOString(),
                application: 'Atomberg Share of Voice AI Agent',
                developer: 'Varun Kadadi',
                version: '1.0'
            },
            analysis_data: currentAnalysisData
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json;charset=utf-8;' });
        
        downloadFile(dataBlob, filename);
        showStatus(`✅ JSON exported successfully: ${filename}`, 'success');
    } catch (error) {
        console.error('JSON export error:', error);
        showStatus('❌ JSON export failed: ' + error.message, 'error');
    }
}

/**
 * Export analysis as CSV
 */
function exportCSV() {
    if (!currentAnalysisData) {
        showStatus('❌ No analysis data to export. Run analysis first.', 'error');
        return;
    }
    
    try {
        showStatus('📊 Preparing CSV export...', 'loading');
        
        let csvContent = '';
        
        // Header
        csvContent += 'Atomberg Share of Voice Analysis Report\n';
        csvContent += `Generated,${new Date().toLocaleString()}\n`;
        csvContent += `Developer,Varun Kadadi\n`;
        csvContent += 'Application,Atomberg SoV AI Agent\n\n';
        
        // Summary metrics
        csvContent += 'SUMMARY METRICS\n';
        csvContent += 'Metric,Value,Unit\n';
        csvContent += `Overall SoV,${(currentAnalysisData.overall_sov || 0).toFixed(2)},%\n`;
        csvContent += `Average Sentiment,${(currentAnalysisData.average_sentiment || 0).toFixed(2)},%\n`;
        csvContent += `Keywords Analyzed,${currentAnalysisData.keywords_analyzed || 0},#\n`;
        csvContent += `Total Mentions,${currentAnalysisData.total_mentions || 0},#\n\n`;
        
        // Keywords table
        csvContent += 'KEYWORD ANALYSIS\n';
        csvContent += 'Keyword,SoV %,Rank,Mentions,Sentiment %\n';
        
        if (currentAnalysisData.keyword_analysis && Array.isArray(currentAnalysisData.keyword_analysis)) {
            currentAnalysisData.keyword_analysis.forEach(kw => {
                csvContent += `"${(kw.keyword || '').replace(/"/g, '""')}",${(kw.sov || 0).toFixed(2)},${kw.rank || '-'},${kw.mentions || 0},${(kw.sentiment || 0).toFixed(2)}\n`;
            });
        }
        
        csvContent += '\n';
        
        // Competitor data
        csvContent += 'COMPETITOR COMPARISON\n';
        csvContent += 'Brand,SoV %\n';
        
        if (currentAnalysisData.competitor_sov && Array.isArray(currentAnalysisData.competitor_sov)) {
            currentAnalysisData.competitor_sov.forEach(comp => {
                csvContent += `"${(comp.brand || '').replace(/"/g, '""')}",${(comp.sov || 0).toFixed(2)}\n`;
            });
        }
        
        // Add footer
        csvContent += '\n\nReport Footer\n';
        csvContent += `Generated By,Atomberg SoV AI Agent\n`;
        csvContent += `Developer,Varun Kadadi\n`;
        csvContent += `Generated Date,${new Date().toLocaleString()}\n`;
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
        const filename = `atomberg_sov_analysis_${timestamp}.csv`;
        const dataBlob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        
        downloadFile(dataBlob, filename);
        showStatus(`✅ CSV exported successfully: ${filename}`, 'success');
    } catch (error) {
        console.error('CSV export error:', error);
        showStatus('❌ CSV export failed: ' + error.message, 'error');
    }
}
        if (currentAnalysisData.keyword_analysis && Array.isArray(currentAnalysisData.keyword_analysis)) {
            currentAnalysisData.keyword_analysis.forEach(kw => {
                csvContent += `"${kw.keyword || ''}",${(kw.sov || 0).toFixed(2)},${kw.rank || '-'},${kw.mentions || 0},${(kw.sentiment || 0).toFixed(2)}\n`;
            });
        }
        
        csvContent += '\n';
        
        // Competitor data
        csvContent += 'COMPETITOR COMPARISON\n';
        csvContent += 'Brand,SoV %\n';
        
        if (currentAnalysisData.competitor_sov && Array.isArray(currentAnalysisData.competitor_sov)) {
            currentAnalysisData.competitor_sov.forEach(comp => {
                csvContent += `"${comp.brand || ''}",${(comp.sov || 0).toFixed(2)}\n`;
            });
        }
        
        // Download
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `atomberg_sov_analysis_${timestamp}.csv`;
        const dataBlob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        
        downloadFile(dataBlob, filename);
        showStatus('✅ Analysis exported as CSV', 'success');
    } catch (error) {
        console.error('CSV export error:', error);
        showStatus('❌ CSV export failed: ' + error.message, 'error');
    }
}

/**
 * Print analysis report
 */
function printReport() {
    if (!currentAnalysisData) {
        showStatus('❌ No analysis data to print', 'error');
        return;
    }
    
    const printWindow = window.open('', '_blank');
    
    let htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Atomberg SoV Analysis Report</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: Arial, sans-serif; color: #333; line-height: 1.6; }
                .container { max-width: 900px; margin: 0 auto; padding: 20px; }
                .header { border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 30px; }
                h1 { color: #667eea; font-size: 32px; margin-bottom: 5px; }
                .timestamp { color: #666; font-size: 12px; }
                h2 { color: #667eea; font-size: 20px; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th { background: #667eea; color: white; padding: 12px; text-align: left; font-weight: bold; }
                td { padding: 10px 12px; border-bottom: 1px solid #eee; }
                tr:nth-child(even) { background: #f7fafc; }
                .metric { display: inline-block; background: #f7fafc; padding: 15px 20px; margin: 10px 10px 10px 0; border-radius: 6px; border-left: 4px solid #667eea; }
                .metric-value { font-size: 24px; font-weight: bold; color: #667eea; }
                .metric-label { font-size: 12px; color: #666; margin-top: 5px; }
                .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }
                @media print {
                    body { background: white; }
                    .metric { page-break-inside: avoid; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Atomberg Share of Voice Analysis</h1>
                    <p class="timestamp">Generated: ${new Date().toLocaleString()}</p>
                </div>
                
                <h2>📊 Summary Metrics</h2>
                <div>
                    <div class="metric">
                        <div class="metric-value">${(currentAnalysisData.overall_sov || 0).toFixed(2)}%</div>
                        <div class="metric-label">Overall SoV</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${(currentAnalysisData.average_sentiment || 0).toFixed(2)}%</div>
                        <div class="metric-label">Avg Sentiment</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${currentAnalysisData.keywords_analyzed || 0}</div>
                        <div class="metric-label">Keywords</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${currentAnalysisData.total_mentions || 0}</div>
                        <div class="metric-label">Total Mentions</div>
                    </div>
                </div>
    `;
    
    // Keywords table
    if (currentAnalysisData.keyword_analysis && Array.isArray(currentAnalysisData.keyword_analysis)) {
        htmlContent += `
            <h2>📈 Keyword Analysis</h2>
            <table>
                <thead>
                    <tr>
                        <th>Keyword</th>
                        <th>SoV %</th>
                        <th>Rank</th>
                        <th>Mentions</th>
                        <th>Sentiment %</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        currentAnalysisData.keyword_analysis.forEach(kw => {
            htmlContent += `
                <tr>
                    <td>${kw.keyword || '-'}</td>
                    <td>${(kw.sov || 0).toFixed(2)}%</td>
                    <td>#${kw.rank || '-'}</td>
                    <td>${kw.mentions || 0}</td>
                    <td>${(kw.sentiment || 0).toFixed(2)}%</td>
                </tr>
            `;
        });
        
        htmlContent += '</tbody></table>';
    }
    
    // Competitor table
    if (currentAnalysisData.competitor_sov && Array.isArray(currentAnalysisData.competitor_sov)) {
        htmlContent += `
            <h2>🏆 Competitor Comparison</h2>
            <table>
                <thead>
                    <tr>
                        <th>Brand</th>
                        <th>SoV %</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        currentAnalysisData.competitor_sov.forEach(comp => {
            htmlContent += `
                <tr>
                    <td>${comp.brand || '-'}</td>
                    <td>${(comp.sov || 0).toFixed(2)}%</td>
                </tr>
            `;
        });
        
        htmlContent += '</tbody></table>';
    }
    
    htmlContent += `
                <div class="footer">
                    <p>This report was generated by the Atomberg Share of Voice Analysis Agent.</p>
                    <p>Data is based on analysis of search results and social media mentions.</p>
                </div>
            </div>
        </body>
        </html>
    `;
    
    printWindow.document.write(htmlContent);
    printWindow.document.close();
    
    setTimeout(() => {
        printWindow.print();
    }, 250);
    
    showStatus('✅ Print dialog opened', 'success');
}

/**
 * Helper function to download file
 */
function downloadFile(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// =====================================================
// DASHBOARD UPDATE
// =====================================================

/**
 * Update dashboard with analysis data
 */
function updateDashboard(data) {
    if (typeof updateDashboard !== 'undefined' && window.updateDashboard instanceof Function) {
        window.updateDashboard(data);
    } else {
        // Fallback: reload initial data
        loadInitialData();
    }
}
