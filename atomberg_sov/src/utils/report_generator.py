"""Report generation module"""
from typing import Dict, Any, List
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate reports from analysis data"""
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.logger = logger
    
    def generate_text_report(self, data: Dict[str, Any], filename: str = "report.txt") -> bool:
        """
        Generate a text-based report.
        
        Args:
            data: Analysis data
            filename: Output filename
            
        Returns:
            Success status
        """
        try:
            filepath = f"{self.output_dir}/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("ATOMBERG SHARE OF VOICE ANALYSIS REPORT\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Write sections
                self._write_executive_summary(f, data)
                self._write_methodology(f)
                self._write_findings(f, data)
                self._write_recommendations(f, data)
            
            self.logger.info(f"Text report generated: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return False
    
    def generate_html_report(self, data: Dict[str, Any], filename: str = "report.html") -> bool:
        """
        Generate an HTML-based report.
        
        Args:
            data: Analysis data
            filename: Output filename
            
        Returns:
            Success status
        """
        try:
            filepath = f"{self.output_dir}/{filename}"
            
            html_content = self._build_html_content(data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report generated: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {str(e)}")
            return False
    
    def _write_executive_summary(self, file, data: Dict[str, Any]):
        """Write executive summary section"""
        file.write("EXECUTIVE SUMMARY\n")
        file.write("-" * 40 + "\n")
        
        sov_data = data.get("sov_analysis", {})
        
        if sov_data:
            file.write(f"\nAtomberg Share of Voice (SoV): {sov_data.get('composite_sov', {}).get('atomberg', 'N/A')}%\n")
            file.write(f"Rank: {sov_data.get('summary', {}).get('rank', 'N/A')} of {sov_data.get('summary', {}).get('total_brands', 'N/A')} brands\n")
        
        file.write("\n" + "=" * 80 + "\n\n")
    
    def _write_methodology(self, file):
        """Write methodology section"""
        file.write("METHODOLOGY\n")
        file.write("-" * 40 + "\n")
        file.write("""
Share of Voice (SoV) is calculated using a composite approach:

1. **Mention-Based SoV**: Percentage of brand mentions in search results
2. **Engagement-Based SoV**: Share of total engagement (likes, comments, shares)
3. **Positive Voice SoV**: Share of positive sentiment mentions

Final SoV Score = (0.4 × Mention SoV) + (0.4 × Engagement SoV) + (0.2 × Positive Voice SoV)

Platforms Analyzed: Google Search, YouTube, Twitter/X, Instagram
""")
        file.write("\n" + "=" * 80 + "\n\n")
    
    def _write_findings(self, file, data: Dict[str, Any]):
        """Write findings section"""
        file.write("KEY FINDINGS\n")
        file.write("-" * 40 + "\n")
        
        sov_data = data.get("sov_analysis", {})
        file.write("\nShare of Voice Breakdown:\n")
        
        composite = sov_data.get("composite_sov", {})
        if composite:
            file.write(f"\n  Atomberg: {composite.get('atomberg', 0)}%\n")
            for competitor, score in composite.get("competitors", {}).items():
                file.write(f"  {competitor}: {score}%\n")
        
        file.write("\n" + "=" * 80 + "\n\n")
    
    def _write_recommendations(self, file, data: Dict[str, Any]):
        """Write recommendations section"""
        file.write("RECOMMENDATIONS TO ATOMBERG TEAM\n")
        file.write("-" * 40 + "\n")
        
        file.write("""
1. Content Strategy
   - Focus on high-engagement content formats that resonate with target audience
   - Leverage platforms with highest Atomberg mention rates
   - Create comparative content highlighting unique features

2. Engagement Enhancement
   - Increase posting frequency on platforms with high engagement potential
   - Implement community engagement strategy for comment sections
   - Use trending hashtags and keywords related to smart fans

3. Sentiment Management
   - Monitor and respond to negative mentions promptly
   - Amplify positive customer testimonials and reviews
   - Address common pain points mentioned in negative content

4. Competitive Analysis
   - Track competitor activity across platforms
   - Identify gaps in competitor messaging
   - Capitalize on market opportunities

5. Measurement & Optimization
   - Track SoV metrics weekly
   - A/B test content and messaging
   - Refine strategy based on engagement patterns
""")
        file.write("\n" + "=" * 80 + "\n\n")
    
    def _build_html_content(self, data: Dict[str, Any]) -> str:
        """Build HTML content for report"""
        sov_data = data.get("sov_analysis", {})
        composite = sov_data.get("composite_sov", {})
        
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atomberg Share of Voice Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        h1 { color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 30px; }
        .sov-score { font-size: 2.5em; color: #007bff; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background: #007bff; color: white; }
        tr:nth-child(even) { background: #f9f9f9; }
        .positive { color: green; }
        .negative { color: red; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Atomberg Share of Voice Analysis Report</h1>
        <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        
        <h2>Executive Summary</h2>
        <p>
            Atomberg's Share of Voice: <span class="sov-score">""" + str(composite.get('atomberg', 0)) + """%</span>
        </p>
        
        <h2>Competitive Analysis</h2>
        <table>
            <tr>
                <th>Brand</th>
                <th>Share of Voice</th>
            </tr>
"""
        
        html += '<tr><td><strong>Atomberg</strong></td><td class="positive">' + str(composite.get('atomberg', 0)) + '%</td></tr>'
        
        for brand, score in sorted(composite.get("competitors", {}).items(), key=lambda x: x[1], reverse=True):
            html += f'<tr><td>{brand}</td><td>{score}%</td></tr>'
        
        html += """
        </table>
        
        <h2>Recommendations</h2>
        <ul>
            <li>Focus on high-engagement content formats</li>
            <li>Increase posting frequency on winning platforms</li>
            <li>Leverage positive sentiment in marketing</li>
            <li>Monitor competitor activities closely</li>
        </ul>
    </div>
</body>
</html>
"""
        return html
