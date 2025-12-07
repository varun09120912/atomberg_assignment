#!/usr/bin/env python3
"""
Interactive CLI for Atomberg SoV Analysis Agent
Allows users to configure brands, keywords, and run analysis interactively
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
from main import SoVAnalysisAgent


class InteractiveSoVCLI:
    """Interactive CLI for SoV Analysis"""
    
    def __init__(self):
        self.config = None
        self.agent = None
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def print_section(self, title: str):
        """Print formatted section"""
        print("\n" + "-" * 80)
        print(f"  {title}")
        print("-" * 80)
    
    def get_brands_from_user(self) -> Dict[str, List[str]]:
        """Get brand configuration from user"""
        self.print_header("BRAND CONFIGURATION")
        
        brand_keywords = {}
        
        # Get primary brand
        print("📌 PRIMARY BRAND")
        primary_brand = input("  Enter primary brand name (default: atomberg): ").strip()
        if not primary_brand:
            primary_brand = "atomberg"
        
        # Get keywords for primary brand
        print(f"\n  Enter keywords for '{primary_brand}'")
        print("  (Leave empty for defaults)")
        keywords_input = input("  Keywords (comma-separated): ").strip()
        
        if keywords_input:
            primary_keywords = [kw.strip() for kw in keywords_input.split(",")]
        else:
            primary_keywords = [
                primary_brand,
                f"smart fan {primary_brand}",
                f"{primary_brand} ceiling fan"
            ]
        
        brand_keywords[primary_brand] = primary_keywords
        
        # Get competitors
        print("\n\n🏢 COMPETITORS")
        competitors_input = input("  Enter competitor brands (comma-separated, or leave empty for defaults): ").strip()
        
        if competitors_input:
            competitors = [brand.strip() for brand in competitors_input.split(",")]
        else:
            competitors = ["havells", "orient", "ortem", "agni", "carro", "luminous"]
        
        for competitor in competitors:
            brand_keywords[competitor] = [competitor]
        
        # Display summary
        self.print_section("BRAND CONFIGURATION SUMMARY")
        for brand, keywords in brand_keywords.items():
            print(f"  ✓ {brand}: {', '.join(keywords)}")
        
        return brand_keywords
    
    def get_search_keywords_from_user(self) -> List[str]:
        """Get search keywords from user"""
        self.print_header("SEARCH KEYWORDS CONFIGURATION")
        
        print("  Enter search keywords to analyze")
        print("  (Leave empty for defaults)")
        keywords_input = input("  Keywords (comma-separated): ").strip()
        
        if keywords_input:
            search_keywords = [kw.strip() for kw in keywords_input.split(",")]
        else:
            search_keywords = [
                "smart fan",
                "smart ceiling fan",
                "WiFi controlled fan",
                "IoT fan",
                "connected ceiling fan"
            ]
        
        # Display summary
        self.print_section("SEARCH KEYWORDS SUMMARY")
        for i, keyword in enumerate(search_keywords, 1):
            print(f"  {i}. {keyword}")
        
        return search_keywords
    
    def get_analysis_options(self) -> Dict[str, Any]:
        """Get analysis options from user"""
        self.print_header("ANALYSIS OPTIONS")
        
        options = {}
        
        # Number of results per keyword
        print("  🔢 Number of results per keyword (default: 20):")
        num_results = input("  Enter number (or press Enter for default): ").strip()
        options['num_results'] = int(num_results) if num_results.isdigit() else 20
        
        # Report format
        print("\n  📄 Report format:")
        print("    1. HTML (default)")
        print("    2. Text")
        print("    3. Both")
        report_format = input("  Select (1-3, or press Enter for default): ").strip()
        
        if report_format == "2":
            options['report_format'] = ['txt']
        elif report_format == "3":
            options['report_format'] = ['html', 'txt']
        else:
            options['report_format'] = ['html']
        
        return options
    
    def confirm_config(self, brand_keywords: Dict[str, List[str]], 
                      search_keywords: List[str], 
                      options: Dict[str, Any]) -> bool:
        """Confirm configuration before proceeding"""
        self.print_section("CONFIGURATION REVIEW")
        
        print(f"\n  Primary Brand: {list(brand_keywords.keys())[0]}")
        print(f"  Number of Competitors: {len(brand_keywords) - 1}")
        print(f"  Search Keywords: {len(search_keywords)}")
        print(f"  Results per Keyword: {options['num_results']}")
        print(f"  Report Format: {', '.join(options['report_format'])}")
        
        print("\n")
        confirm = input("  Proceed with analysis? (yes/no): ").strip().lower()
        return confirm in ['yes', 'y']
    
    def run_analysis(self, brand_keywords: Dict[str, List[str]], 
                    search_keywords: List[str]):
        """Run the SoV analysis"""
        self.print_header("RUNNING ANALYSIS")
        
        print("  Initializing agent...")
        self.agent = SoVAnalysisAgent(
            brand_keywords=brand_keywords,
            search_keywords=search_keywords
        )
        
        print("  Starting keyword analysis...")
        results = self.agent.analyze_multiple_keywords()
        
        print("  Saving analysis results...")
        self.agent.save_analysis(results)
        
        print("  Generating reports...")
        for fmt in ['html', 'txt']:
            self.agent.generate_report(results, format=fmt)
        
        self.print_results(results)
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Print analysis results"""
        self.print_section("ANALYSIS RESULTS")
        
        insights = results.get("aggregate_insights", {})
        
        print(f"\n  📊 Overall Share of Voice: {insights.get('average_sov', 0)}%")
        print(f"  📈 Keywords Analyzed: {insights.get('keywords_analyzed', 0)}")
        
        if insights.get('top_keywords'):
            print(f"\n  🏆 Top Keywords by SoV:")
            for keyword, sov in insights.get('top_keywords', []):
                print(f"     • {keyword}: {sov}%")
        
        print(f"\n  📋 Detailed Results:")
        for keyword, analysis in results.get("keyword_analyses", {}).items():
            sov_data = analysis.get("sov_analysis", {})
            sentiment = analysis.get("sentiment_analysis", {})
            
            print(f"\n     Keyword: '{keyword}'")
            print(f"       SoV: {sov_data.get('composite_sov', {}).get('atomberg', 0)}%")
            print(f"       Rank: {sov_data.get('summary', {}).get('rank', 'N/A')}")
            print(f"       Positive Sentiment: {sentiment.get('positive_percentage', 0)}%")
    
    def show_menu(self) -> str:
        """Show main menu and get user choice"""
        self.print_header("ATOMBERG SOV ANALYSIS AGENT")
        
        print("  What would you like to do?")
        print("\n  1. Run new analysis with custom configuration")
        print("  2. Run analysis with default configuration")
        print("  3. View saved analysis results")
        print("  4. Exit")
        
        choice = input("\n  Select (1-4): ").strip()
        return choice
    
    def view_saved_results(self):
        """View previously saved analysis results"""
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        analysis_file = os.path.join(data_dir, 'analysis.json')
        
        if not os.path.exists(analysis_file):
            print("\n  ❌ No saved analysis found!")
            return
        
        try:
            with open(analysis_file, 'r') as f:
                results = json.load(f)
            
            self.print_results(results)
            
        except Exception as e:
            print(f"\n  ❌ Error loading analysis: {e}")
    
    def run_interactive(self):
        """Run interactive CLI"""
        while True:
            self.clear_screen()
            choice = self.show_menu()
            
            if choice == "1":
                # Custom configuration
                brand_keywords = self.get_brands_from_user()
                search_keywords = self.get_search_keywords_from_user()
                options = self.get_analysis_options()
                
                if self.confirm_config(brand_keywords, search_keywords, options):
                    results = self.run_analysis(brand_keywords, search_keywords)
                    
                    self.print_section("NEXT STEPS")
                    print("  ✅ Analysis complete!")
                    print(f"  📁 Reports saved to: output/")
                    print(f"  💾 Data saved to: data/analysis.json")
                    print("\n  Press Enter to continue...")
                    input()
                else:
                    print("\n  Analysis cancelled.")
                    input("  Press Enter to continue...")
            
            elif choice == "2":
                # Default configuration
                brand_keywords = {
                    "atomberg": ["atomberg", "smart fan atomberg", "atomberg ceiling fan"],
                    "havells": ["havells"],
                    "orient": ["orient"],
                    "ortem": ["ortem"],
                    "agni": ["agni"],
                    "carro": ["carro"],
                    "luminous": ["luminous"],
                }
                search_keywords = [
                    "smart fan",
                    "smart ceiling fan",
                    "WiFi controlled fan",
                ]
                
                results = self.run_analysis(brand_keywords, search_keywords)
                
                self.print_section("NEXT STEPS")
                print("  ✅ Analysis complete!")
                print(f"  📁 Reports saved to: output/")
                print(f"  💾 Data saved to: data/analysis.json")
                print("\n  Press Enter to continue...")
                input()
            
            elif choice == "3":
                # View saved results
                self.view_saved_results()
                print("\n  Press Enter to continue...")
                input()
            
            elif choice == "4":
                # Exit
                print("\n  👋 Goodbye!")
                break
            
            else:
                print("\n  ❌ Invalid choice. Please try again.")
                input("  Press Enter to continue...")


def main():
    """Main entry point"""
    cli = InteractiveSoVCLI()
    cli.run_interactive()


if __name__ == "__main__":
    main()
