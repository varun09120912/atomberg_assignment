"""
Flask web server for Atomberg SoV AI Agent
Provides REST API and responsive web dashboard
"""
import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging

# Import our AI agent
from main import SoVAnalysisAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize the agent with default config
agent = SoVAnalysisAgent()

# Store results in memory
analysis_results = None
last_update = None

# Try to load existing analysis from file
def load_existing_analysis():
    """Load previously saved analysis from file"""
    global analysis_results, last_update
    
    analysis_file = os.path.join(os.path.dirname(__file__), 'data', 'analysis.json')
    if os.path.exists(analysis_file):
        try:
            with open(analysis_file, 'r') as f:
                raw_data = json.load(f)
            
            # Transform raw data to UI format
            analysis_results = transform_analysis_data(raw_data)
            last_update = datetime.now().isoformat()
            print(f"✅ Loaded existing analysis from {analysis_file}")
            return True
        except Exception as e:
            print(f"⚠️  Could not load analysis file: {e}")
            return False
    return False

def transform_analysis_data(raw_data):
    """Transform raw analysis data to UI format"""
    if not raw_data or 'keyword_analyses' not in raw_data:
        return raw_data
    
    keyword_analyses = raw_data.get('keyword_analyses', {})
    
    # Calculate aggregate metrics
    sov_values = []
    sentiment_values = []
    keywords_count = len(keyword_analyses)
    competitors = {}
    keyword_analysis = {}
    
    for keyword, data in keyword_analyses.items():
        # Get SoV summary
        sov_summary = data.get('sov_analysis', {}).get('summary', {})
        atomberg_sov = sov_summary.get('atomberg_sov', 0)
        sov_values.append(atomberg_sov)
        
        # Get sentiment
        sentiment = data.get('sentiment_analysis', {})
        sentiment_values.append(sentiment.get('positive_percentage', 0))
        
        # Get competitor data
        for comp, value in sov_summary.get('competitor_rankings', []):
            if comp not in competitors:
                competitors[comp] = {'sov_percentage': 0, 'total_mentions': 0, 'positive_percentage': 0}
            competitors[comp]['sov_percentage'] = value
        
        # Get keyword analysis
        keyword_analysis[keyword] = {
            'atomberg_sov_percentage': atomberg_sov,
            'atomberg_mentions': data.get('brand_analysis', {}).get('mentions', {}).get('atomberg', 0),
            'atomberg_engagement': data.get('engagement_analysis', {}).get('avg_engagement_per_item', 0),
        }
    
    # Calculate averages
    avg_sov = sum(sov_values) / len(sov_values) if sov_values else 0
    avg_sentiment = sum(sentiment_values) / len(sentiment_values) if sentiment_values else 0
    
    # Build transformed data
    transformed = {
        'sov_metrics': {
            'atomberg_sov_percentage': round(avg_sov, 2),
            'market_rank': 1,
            'positive_sentiment_percentage': round(avg_sentiment, 2),
            'keywords_analyzed': keywords_count,
            'neutral_sentiment_percentage': round(100 - avg_sentiment, 2),
        },
        'competitors': competitors,
        'keyword_analysis': keyword_analysis,
        'raw_data': raw_data
    }
    
    return transformed

# Load analysis on startup
load_existing_analysis()

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/analysis', methods=['GET'])
def get_analysis():
    """Get cached analysis results"""
    global analysis_results, last_update
    
    if analysis_results is None:
        return jsonify({"error": "No analysis available. Run analysis first."}), 404
    
    return jsonify({
        "data": analysis_results,
        "last_update": last_update,
        "status": "success"
    })

@app.route('/api/run-analysis', methods=['POST'])
def run_analysis():
    """Run the SoV analysis"""
    global analysis_results, last_update
    
    try:
        # Get optional keywords from request
        data = request.get_json() or {}
        keywords = data.get('keywords', None)
        
        # Run analysis
        if keywords:
            results = agent.analyze_multiple_keywords(keywords)
        else:
            results = agent.analyze_multiple_keywords()
        
        # Transform to UI format
        transformed_results = transform_analysis_data(results)
        
        # Store results
        analysis_results = transformed_results
        last_update = datetime.now().isoformat()
        
        # Save to file
        agent.save_analysis(results)
        
        return jsonify({
            "status": "success",
            "message": "Analysis completed successfully",
            "data": transformed_results,
            "timestamp": last_update
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/insights', methods=['GET'])
def get_insights():
    """Get aggregate insights"""
    global analysis_results
    
    if analysis_results is None:
        return jsonify({"error": "No analysis available"}), 404
    
    insights = analysis_results.get('aggregate_insights', {})
    
    return jsonify({
        "average_sov": insights.get('average_sov', 0),
        "keywords_analyzed": insights.get('keywords_analyzed', 0),
        "top_keywords": insights.get('top_keywords', []),
        "status": "success"
    })

@app.route('/api/sov-breakdown', methods=['GET'])
def get_sov_breakdown():
    """Get detailed SoV breakdown by keyword"""
    global analysis_results
    
    if analysis_results is None:
        return jsonify({"error": "No analysis available"}), 404
    
    breakdown = {}
    analyses = analysis_results.get('keyword_analyses', {})
    
    for keyword, analysis in analyses.items():
        sov_data = analysis.get('sov_analysis', {})
        composite = sov_data.get('composite_sov', {})
        breakdown[keyword] = {
            "atomberg_sov": composite.get('atomberg', 0),
            "competitors": composite.get('competitors', {}),
            "rank": sov_data.get('summary', {}).get('rank', 0)
        }
    
    return jsonify({
        "breakdown": breakdown,
        "status": "success"
    })

@app.route('/api/sentiment-analysis', methods=['GET'])
def get_sentiment_analysis():
    """Get sentiment analysis data"""
    global analysis_results
    
    if analysis_results is None:
        return jsonify({"error": "No analysis available"}), 404
    
    sentiment_data = {}
    analyses = analysis_results.get('keyword_analyses', {})
    
    for keyword, analysis in analyses.items():
        sentiment = analysis.get('sentiment_analysis', {})
        sentiment_data[keyword] = {
            "positive": sentiment.get('positive_percentage', 0),
            "negative": sentiment.get('negative_percentage', 0),
            "neutral": sentiment.get('neutral_percentage', 0)
        }
    
    return jsonify({
        "sentiment": sentiment_data,
        "status": "success"
    })

@app.route('/api/engagement-metrics', methods=['GET'])
def get_engagement_metrics():
    """Get engagement metrics data"""
    global analysis_results
    
    if analysis_results is None:
        return jsonify({"error": "No analysis available"}), 404
    
    engagement_data = {}
    analyses = analysis_results.get('keyword_analyses', {})
    
    for keyword, analysis in analyses.items():
        engagement = analysis.get('engagement_analysis', {})
        engagement_data[keyword] = {
            "total_engagement": engagement.get('total_engagement', 0),
            "avg_likes": engagement.get('avg_likes_per_item', 0),
            "total_views": engagement.get('total_views', 0)
        }
    
    return jsonify({
        "engagement": engagement_data,
        "status": "success"
    })

@app.route('/api/competitors', methods=['GET'])
def get_competitors():
    """Get competitor data"""
    global analysis_results
    
    if analysis_results is None:
        return jsonify({"error": "No analysis available"}), 404
    
    competitors = {}
    analyses = analysis_results.get('keyword_analyses', {})
    
    if analyses:
        first_analysis = next(iter(analyses.values()), {})
        sov_data = first_analysis.get('sov_analysis', {})
        composite = sov_data.get('composite_sov', {})
        competitors = composite.get('competitors', {})
    
    return jsonify({
        "competitors": competitors,
        "atomberg": next(iter(analyses.values()), {}).get('sov_analysis', {}).get('composite_sov', {}).get('atomberg', 0) if analyses else 0,
        "status": "success"
    })

@app.route('/api/export-json', methods=['GET'])
def export_json():
    """Export analysis as JSON"""
    global analysis_results
    
    if analysis_results is None:
        return jsonify({"error": "No analysis available"}), 404
    
    return jsonify(analysis_results)

@app.route('/api/user-search', methods=['POST'])
def user_search():
    """Handle user-initiated search with custom parameters"""
    global analysis_results, last_update
    
    try:
        data = request.get_json()
        
        # Validate input
        keywords = data.get('keywords', [])
        num_results = int(data.get('num_results', 10))
        analysis_type = data.get('analysis_type', 'full')
        
        if not keywords or not isinstance(keywords, list):
            return jsonify({
                "success": False,
                "message": "Invalid keywords format. Expected list of strings."
            }), 400
        
        if num_results < 1 or num_results > 50:
            num_results = min(max(num_results, 1), 50)
        
        # Run analysis with user parameters
        print(f"\n🔍 Running user-initiated analysis...")
        print(f"   Keywords: {', '.join(keywords)}")
        print(f"   Results per keyword: {num_results}")
        print(f"   Analysis type: {analysis_type}")
        
        results = agent.analyze_multiple_keywords(
            keywords=keywords,
            num_results=num_results,
            scraper_type='mock'  # Use mock scraper by default for demo
        )
        
        # Transform results for UI
        analysis_results = transform_analysis_data(results)
        last_update = datetime.now().isoformat()
        
        # Save to file for persistence
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, 'analysis.json'), 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Analysis complete. Results saved.")
        
        return jsonify({
            "success": True,
            "message": f"Analysis complete for {len(keywords)} keyword(s)",
            "data": build_ui_format(analysis_results, results),
            "timestamp": last_update
        })
    
    except Exception as e:
        print(f"❌ Error in user search: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Error processing search: {str(e)}"
        }), 500

def build_ui_format(transformed_data, raw_data):
    """Build UI-friendly format from analysis data"""
    keyword_analyses = raw_data.get('keyword_analyses', {})
    
    # Calculate metrics
    sov_values = []
    sentiment_values = []
    all_mentions = 0
    competitors_data = {}
    keyword_analysis_list = []
    
    for keyword, data in keyword_analyses.items():
        sov_summary = data.get('sov_analysis', {}).get('summary', {})
        atomberg_sov = sov_summary.get('atomberg_sov', 0)
        sov_values.append(atomberg_sov)
        
        sentiment = data.get('sentiment_analysis', {})
        sentiment_values.append(sentiment.get('positive_percentage', 0))
        
        brand_data = data.get('brand_analysis', {})
        mentions = brand_data.get('mentions', {}).get('atomberg', 0)
        all_mentions += mentions
        
        # Keyword analysis entry
        keyword_analysis_list.append({
            'keyword': keyword,
            'sov': round(atomberg_sov, 2),
            'rank': sov_summary.get('rank', 0),
            'mentions': mentions,
            'sentiment': round(sentiment.get('positive_percentage', 0), 2)
        })
        
        # Competitor data
        for comp_name, comp_sov in sov_summary.get('competitor_rankings', []):
            if comp_name not in competitors_data:
                competitors_data[comp_name] = 0
            competitors_data[comp_name] = comp_sov
    
    # Build response
    return {
        'overall_sov': round(sum(sov_values) / len(sov_values) if sov_values else 0, 2),
        'average_sentiment': round(sum(sentiment_values) / len(sentiment_values) if sentiment_values else 0, 2),
        'keywords_analyzed': len(keyword_analyses),
        'total_mentions': all_mentions,
        'keyword_analysis': keyword_analysis_list,
        'competitor_sov': [{'brand': k, 'sov': round(v, 2)} for k, v in competitors_data.items()],
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "has_analysis": analysis_results is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/status', methods=['GET'])
def status():
    """Get current status"""
    return jsonify({
        "analysis_available": analysis_results is not None,
        "last_update": last_update,
        "status": "ready"
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Run Flask app
    print("\n" + "="*70)
    print("ATOMBERG SoV AI AGENT - WEB DASHBOARD")
    print("="*70)
    print("\n🚀 Starting Flask server...")
    print("📱 Open browser: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000/")
    print("🔌 API: http://localhost:5000/api/")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
