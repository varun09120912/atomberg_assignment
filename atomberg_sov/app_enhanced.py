"""
Enhanced Flask web server for Atomberg SoV AI Agent
Provides REST API and responsive web dashboard
"""
import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import logging
from io import BytesIO
import csv

# Import our AI agent
from main import SoVAnalysisAgent
from src.utils import ReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global agent instance
agent = None
analysis_cache = None

def get_agent():
    """Get or create agent instance"""
    global agent
    if agent is None:
        agent = SoVAnalysisAgent()
    return agent

# =====================
# ROUTES
# =====================

@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('dashboard_new.html')

@app.route('/api/analysis', methods=['GET'])
def get_analysis():
    """Get cached analysis or load from file"""
    global analysis_cache
    
    try:
        # Try to load from file
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        analysis_file = os.path.join(data_dir, 'analysis.json')
        
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r') as f:
                analysis_cache = json.load(f)
                logger.info('Loaded analysis from file')
                return jsonify(analysis_cache)
        
        # Return demo data if no file exists
        logger.warning('No analysis file found, returning demo data')
        return jsonify(get_demo_data())
        
    except Exception as e:
        logger.error(f'Error loading analysis: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def run_analysis():
    """Run analysis with custom configuration"""
    global analysis_cache
    
    try:
        data = request.json
        logger.info(f'Received analysis request: {data}')
        
        # Extract configuration
        brand_keywords = data.get('brand_keywords', {})
        search_keywords = data.get('search_keywords', [])
        
        # Create agent with custom config
        custom_agent = SoVAnalysisAgent(
            brand_keywords=brand_keywords,
            search_keywords=search_keywords
        )
        
        logger.info('Running analysis...')
        # Run analysis
        results = custom_agent.analyze_multiple_keywords()
        
        # Save results
        custom_agent.save_analysis(results)
        
        # Cache results
        analysis_cache = results
        
        logger.info('Analysis completed successfully')
        return jsonify(results)
        
    except Exception as e:
        logger.error(f'Error running analysis: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get agent status"""
    try:
        agent = get_agent()
        return jsonify({
            'status': 'ready',
            'agent': 'initialized',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get default configuration"""
    return jsonify({
        'default_brands': {
            'atomberg': ['atomberg', 'smart fan atomberg', 'atomberg ceiling fan'],
            'havells': ['havells'],
            'orient': ['orient'],
            'ortem': ['ortem'],
            'agni': ['agni'],
            'carro': ['carro'],
            'luminous': ['luminous']
        },
        'default_keywords': [
            'smart fan',
            'smart ceiling fan',
            'WiFi controlled fan'
        ]
    })

@app.route('/api/demo', methods=['GET'])
def get_demo():
    """Get demo data"""
    return jsonify(get_demo_data())

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate report in requested format"""
    try:
        data = request.json
        analysis_data = data.get('analysis_data', {})
        report_format = data.get('format', 'html')  # html, json, csv, txt
        
        if report_format == 'html':
            report_html = generate_html_report(analysis_data)
            return jsonify({
                'format': 'html',
                'content': report_html,
                'filename': f'atomberg_sov_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            })
        
        elif report_format == 'json':
            return jsonify({
                'format': 'json',
                'content': analysis_data,
                'filename': f'atomberg_sov_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            })
        
        elif report_format == 'csv':
            csv_content = generate_csv_report(analysis_data)
            return jsonify({
                'format': 'csv',
                'content': csv_content,
                'filename': f'atomberg_sov_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            })
        
        elif report_format == 'txt':
            txt_content = generate_txt_report(analysis_data)
            return jsonify({
                'format': 'txt',
                'content': txt_content,
                'filename': f'atomberg_sov_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            })
        
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        logger.error(f'Error generating report: {e}')
        return jsonify({'error': str(e)}), 500

# =====================
# HELPER FUNCTIONS
# =====================

def generate_html_report(data):
    """Generate HTML report from analysis data"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atomberg Share of Voice Report</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #1e3a8a; border-bottom: 4px solid #2563eb; padding-bottom: 15px; margin-top: 0; }
        h2 { color: #1e293b; margin-top: 30px; border-left: 4px solid #2563eb; padding-left: 10px; }
        h3 { color: #475569; }
        .summary-box { background: #dbeafe; border-left: 4px solid #2563eb; padding: 15px; margin: 15px 0; border-radius: 4px; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; }
        .metric-label { font-size: 0.9em; color: #64748b; font-weight: 600; }
        .metric-value { font-size: 2em; color: #2563eb; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #2563eb; color: white; padding: 12px; text-align: left; font-weight: 600; }
        td { padding: 10px 12px; border-bottom: 1px solid #e2e8f0; }
        tr:hover { background: #f8fafc; }
        .positive { color: #10b981; font-weight: bold; }
        .negative { color: #ef4444; font-weight: bold; }
        .neutral { color: #64748b; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #e2e8f0; font-size: 0.9em; color: #64748b; text-align: center; }
        .chart-section { margin: 30px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Atomberg Share of Voice Analysis Report</h1>
        <p><strong>Generated:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        
        <h2>📈 Executive Summary</h2>
        <div class="summary-box">
"""
    
    # Get aggregate insights
    insights = data.get('aggregate_insights', {})
    avg_sov = insights.get('average_sov', 0)
    keywords_analyzed = insights.get('keywords_analyzed', 0)
    top_keywords = insights.get('top_keywords', [])
    
    html += f"""
            <div class="metric">
                <div class="metric-label">Average SoV</div>
                <div class="metric-value">{avg_sov:.1f}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Keywords Analyzed</div>
                <div class="metric-value">{keywords_analyzed}</div>
            </div>
        </div>
"""
    
    # Keyword Details
    html += "<h2>🔍 Keyword Analysis</h2>"
    html += """
        <table>
            <tr>
                <th>Keyword</th>
                <th>Atomberg SoV %</th>
                <th>Rank</th>
                <th>Total Mentions</th>
                <th>Positive Sentiment</th>
                <th>Engagement</th>
            </tr>
"""
    
    keyword_analyses = data.get('keyword_analyses', {})
    for keyword, analysis in keyword_analyses.items():
        sov = analysis.get('sov_analysis', {}).get('summary', {}).get('atomberg_sov', 0)
        rank = analysis.get('sov_analysis', {}).get('summary', {}).get('rank', '-')
        mentions = analysis.get('brand_analysis', {}).get('mentions', {}).get('atomberg', 0)
        sentiment = analysis.get('sentiment_analysis', {})
        positive = sentiment.get('positive_percentage', 0)
        engagement = analysis.get('engagement_analysis', {}).get('total_engagement', 0)
        
        html += f"""
            <tr>
                <td><strong>{keyword}</strong></td>
                <td>{sov:.1f}%</td>
                <td>{rank}</td>
                <td>{mentions}</td>
                <td><span class="positive">+{positive}%</span></td>
                <td>{engagement}</td>
            </tr>
"""
    
    html += """
        </table>
"""
    
    # Competitive Analysis
    html += "<h2>🏆 Competitive Analysis</h2>"
    html += """
        <table>
            <tr>
                <th>Keyword</th>
                <th>Atomberg</th>
                <th>Competitor Rankings</th>
            </tr>
"""
    
    for keyword, analysis in keyword_analyses.items():
        atomberg_sov = analysis.get('sov_analysis', {}).get('summary', {}).get('atomberg_sov', 0)
        competitors = analysis.get('sov_analysis', {}).get('summary', {}).get('competitor_rankings', [])
        
        competitor_str = ', '.join([f"{comp[0]}: {comp[1]}%" for comp in competitors[:3]])
        
        html += f"""
            <tr>
                <td><strong>{keyword}</strong></td>
                <td><span class="positive">{atomberg_sov:.1f}%</span></td>
                <td>{competitor_str}</td>
            </tr>
"""
    
    html += """
        </table>
"""
    
    # Sentiment Summary
    html += "<h2>💬 Sentiment Analysis Summary</h2>"
    html += """
        <table>
            <tr>
                <th>Keyword</th>
                <th>Positive</th>
                <th>Neutral</th>
                <th>Negative</th>
            </tr>
"""
    
    for keyword, analysis in keyword_analyses.items():
        sentiment = analysis.get('sentiment_analysis', {})
        pos = sentiment.get('positive_percentage', 0)
        neu = sentiment.get('neutral_percentage', 0)
        neg = sentiment.get('negative_percentage', 0)
        
        html += f"""
            <tr>
                <td><strong>{keyword}</strong></td>
                <td><span class="positive">+{pos}%</span></td>
                <td><span class="neutral">={neu}%</span></td>
                <td><span class="negative">-{neg}%</span></td>
            </tr>
"""
    
    html += """
        </table>
"""
    
    # Recommendations
    html += """
        <h2>💡 Recommendations</h2>
        <ul>
            <li><strong>Content Strategy:</strong> Focus on high-engagement content formats that resonate with target audience</li>
            <li><strong>Sentiment Management:</strong> Monitor and respond to negative mentions promptly</li>
            <li><strong>Engagement Enhancement:</strong> Increase posting frequency on platforms with highest engagement potential</li>
            <li><strong>Competitive Analysis:</strong> Track competitor activity and identify market opportunities</li>
            <li><strong>Measurement:</strong> Track SoV metrics weekly and refine strategy based on engagement patterns</li>
        </ul>
        
        <div class="footer">
            <p><strong>Atomberg Share of Voice Analysis</strong></p>
            <p>Report Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            <p>© 2024 Atomberg Technologies. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
    return html

def generate_txt_report(data):
    """Generate text report from analysis data"""
    txt = """
╔════════════════════════════════════════════════════════════════════╗
║    ATOMBERG SHARE OF VOICE ANALYSIS REPORT                        ║
╚════════════════════════════════════════════════════════════════════╝

Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

═══════════════════════════════════════════════════════════════════════
EXECUTIVE SUMMARY
═══════════════════════════════════════════════════════════════════════
"""
    
    insights = data.get('aggregate_insights', {})
    txt += f"""
Average Share of Voice (SoV): {insights.get('average_sov', 0):.1f}%
Keywords Analyzed: {insights.get('keywords_analyzed', 0)}

"""
    
    # Keyword Analysis
    txt += """═══════════════════════════════════════════════════════════════════════
KEYWORD ANALYSIS
═══════════════════════════════════════════════════════════════════════

"""
    
    keyword_analyses = data.get('keyword_analyses', {})
    for keyword, analysis in keyword_analyses.items():
        sov = analysis.get('sov_analysis', {}).get('summary', {}).get('atomberg_sov', 0)
        rank = analysis.get('sov_analysis', {}).get('summary', {}).get('rank', '-')
        mentions = analysis.get('brand_analysis', {}).get('mentions', {}).get('atomberg', 0)
        sentiment = analysis.get('sentiment_analysis', {})
        pos = sentiment.get('positive_percentage', 0)
        
        txt += f"""
Keyword: {keyword}
  • Share of Voice: {sov:.1f}%
  • Rank: {rank}
  • Mentions: {mentions}
  • Positive Sentiment: {pos}%

"""
    
    # Competitive Analysis
    txt += """═══════════════════════════════════════════════════════════════════════
COMPETITIVE ANALYSIS
═══════════════════════════════════════════════════════════════════════

"""
    
    for keyword, analysis in keyword_analyses.items():
        atomberg_sov = analysis.get('sov_analysis', {}).get('summary', {}).get('atomberg_sov', 0)
        competitors = analysis.get('sov_analysis', {}).get('summary', {}).get('competitor_rankings', [])
        
        txt += f"\n{keyword.upper()}:\n"
        txt += f"  Atomberg: {atomberg_sov:.1f}%\n"
        
        for comp, score in competitors[:5]:
            txt += f"  {comp}: {score}%\n"
    
    # Recommendations
    txt += """

═══════════════════════════════════════════════════════════════════════
RECOMMENDATIONS
═══════════════════════════════════════════════════════════════════════

1. CONTENT STRATEGY
   - Focus on high-engagement content formats
   - Leverage platforms with highest mention rates
   - Create comparative content highlighting unique features

2. SENTIMENT MANAGEMENT
   - Monitor and respond to negative mentions promptly
   - Amplify positive customer testimonials
   - Address common pain points

3. ENGAGEMENT ENHANCEMENT
   - Increase posting frequency on winning platforms
   - Implement community engagement strategy
   - Use trending hashtags and keywords

4. COMPETITIVE ANALYSIS
   - Track competitor activity across platforms
   - Identify gaps in competitor messaging
   - Capitalize on market opportunities

5. MEASUREMENT & OPTIMIZATION
   - Track SoV metrics weekly
   - A/B test content and messaging
   - Refine strategy based on patterns

═══════════════════════════════════════════════════════════════════════
Report Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
© 2024 Atomberg Technologies
═══════════════════════════════════════════════════════════════════════
"""
    return txt

def generate_csv_report(data):
    """Generate CSV report from analysis data"""
    output = []
    
    # Header
    output.append(['Atomberg Share of Voice Analysis Report'])
    output.append(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    output.append([])
    
    # Summary
    insights = data.get('aggregate_insights', {})
    output.append(['SUMMARY'])
    output.append(['Average SoV %', insights.get('average_sov', 0)])
    output.append(['Keywords Analyzed', insights.get('keywords_analyzed', 0)])
    output.append([])
    
    # Keyword Analysis
    output.append(['KEYWORD ANALYSIS'])
    output.append(['Keyword', 'Atomberg SoV %', 'Rank', 'Mentions', 'Positive %', 'Engagement'])
    
    keyword_analyses = data.get('keyword_analyses', {})
    for keyword, analysis in keyword_analyses.items():
        sov = analysis.get('sov_analysis', {}).get('summary', {}).get('atomberg_sov', 0)
        rank = analysis.get('sov_analysis', {}).get('summary', {}).get('rank', '-')
        mentions = analysis.get('brand_analysis', {}).get('mentions', {}).get('atomberg', 0)
        sentiment = analysis.get('sentiment_analysis', {})
        pos = sentiment.get('positive_percentage', 0)
        engagement = analysis.get('engagement_analysis', {}).get('total_engagement', 0)
        
        output.append([keyword, f'{sov:.1f}', rank, mentions, f'{pos}', engagement])
    
    output.append([])
    
    # Competitive Analysis
    output.append(['COMPETITIVE ANALYSIS'])
    for keyword, analysis in keyword_analyses.items():
        atomberg_sov = analysis.get('sov_analysis', {}).get('summary', {}).get('atomberg_sov', 0)
        competitors = analysis.get('sov_analysis', {}).get('summary', {}).get('competitor_rankings', [])
        
        output.append([keyword])
        output.append(['Atomberg', f'{atomberg_sov:.1f}%'])
        for comp, score in competitors[:5]:
            output.append([comp, f'{score}%'])
        output.append([])
    
    # Convert to CSV string
    import io
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerows(output)
    return csv_buffer.getvalue()

def get_demo_data():
    """Return demo analysis data"""
    return {
        'aggregate_insights': {
            'average_sov': 53.5,
            'keywords_analyzed': 3,
            'top_keywords': [
                ['smart fan', 55.2],
                ['WiFi fan', 52.8],
                ['ceiling fan', 52.5]
            ]
        },
        'keyword_analyses': {
            'smart fan': {
                'keyword': 'smart fan',
                'sov_analysis': {
                    'summary': {
                        'atomberg_sov': 55.2,
                        'rank': 2,
                        'total_brands': 6,
                        'competitor_rankings': [
                            ['havells', 45],
                            ['orient', 30],
                            ['agni', 15],
                            ['carro', 5],
                            ['luminous', 5]
                        ]
                    }
                },
                'sentiment_analysis': {
                    'positive_percentage': 65,
                    'neutral_percentage': 25,
                    'negative_percentage': 10,
                    'positive_count': 130,
                    'neutral_count': 50,
                    'negative_count': 20
                },
                'brand_analysis': {
                    'mentions': {
                        'atomberg': 120,
                        'havells': 90,
                        'orient': 60,
                        'agni': 30,
                        'carro': 10,
                        'luminous': 10
                    }
                },
                'engagement_analysis': {
                    'total_engagement': 2500,
                    'avg_engagement_per_item': 125
                }
            },
            'WiFi fan': {
                'keyword': 'WiFi fan',
                'sov_analysis': {
                    'summary': {
                        'atomberg_sov': 52.8,
                        'rank': 2,
                        'total_brands': 6,
                        'competitor_rankings': [
                            ['havells', 48],
                            ['orient', 32],
                            ['agni', 12],
                            ['carro', 4],
                            ['luminous', 4]
                        ]
                    }
                },
                'sentiment_analysis': {
                    'positive_percentage': 70,
                    'neutral_percentage': 20,
                    'negative_percentage': 10,
                    'positive_count': 140,
                    'neutral_count': 40,
                    'negative_count': 20
                },
                'brand_analysis': {
                    'mentions': {
                        'atomberg': 110,
                        'havells': 95,
                        'orient': 65,
                        'agni': 25,
                        'carro': 8,
                        'luminous': 8
                    }
                },
                'engagement_analysis': {
                    'total_engagement': 2400,
                    'avg_engagement_per_item': 120
                }
            },
            'ceiling fan': {
                'keyword': 'ceiling fan',
                'sov_analysis': {
                    'summary': {
                        'atomberg_sov': 52.5,
                        'rank': 2,
                        'total_brands': 6,
                        'competitor_rankings': [
                            ['havells', 46],
                            ['orient', 31],
                            ['agni', 14],
                            ['carro', 6],
                            ['luminous', 6]
                        ]
                    }
                },
                'sentiment_analysis': {
                    'positive_percentage': 62,
                    'neutral_percentage': 28,
                    'negative_percentage': 10,
                    'positive_count': 124,
                    'neutral_count': 56,
                    'negative_count': 20
                },
                'brand_analysis': {
                    'mentions': {
                        'atomberg': 105,
                        'havells': 92,
                        'orient': 62,
                        'agni': 28,
                        'carro': 12,
                        'luminous': 12
                    }
                },
                'engagement_analysis': {
                    'total_engagement': 2300,
                    'avg_engagement_per_item': 115
                }
            }
        }
    }

# =====================
# ERROR HANDLERS
# =====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# =====================
# START SERVER
# =====================

if __name__ == '__main__':
    logger.info('Starting Atomberg SOV Dashboard Server...')
    logger.info('Visit http://localhost:5000')
    
    # Create necessary directories
    os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'output'), exist_ok=True)
    
    # Run Flask server
    app.run(debug=True, host='0.0.0.0', port=5000)
