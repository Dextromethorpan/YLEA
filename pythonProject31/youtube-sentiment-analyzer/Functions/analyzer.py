"""
Main YouTube Sentiment Analyzer class
"""

import os
from datetime import datetime
from .sentiment_analysis import EMOTION_KEYWORDS, analyze_sentiment, analyze_emotions
from .csv_processing import load_csv_and_process
from .visualization import create_visualizations
from .reporting import generate_report, save_results


class YouTubeSentimentAnalyzer:
    def __init__(self, csv_file_path, output_folder=None):
        """
        Initialize the YouTube Sentiment Analyzer

        Args:
            csv_file_path (str): Path to the CSV file containing video IDs/URLs
            output_folder (str): Path to folder where all output files will be saved
        """
        self.csv_file_path = csv_file_path
        self.results = []
        self.emotion_keywords = EMOTION_KEYWORDS
        
        # Set up output folder
        if output_folder is None:
            csv_name = os.path.splitext(os.path.basename(csv_file_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_folder = f"analysis_results_{csv_name}_{timestamp}"
        else:
            self.output_folder = output_folder
            
        # Create output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)
        print(f"📁 Output folder: {self.output_folder}")

    def run_analysis(self):
        """Run the complete analysis pipeline"""
        print("🚀 Starting YouTube Sentiment Analysis...")
        print("=" * 50)

        # Load and process CSV
        success, results = load_csv_and_process(
            self.csv_file_path, 
            analyze_sentiment, 
            analyze_emotions
        )
        
        if not success:
            print("❌ Analysis failed - could not process videos or CSV is empty")
            return False

        if not results:
            print("❌ No videos were successfully processed")
            return False

        # Store results
        self.results = results

        print("\n🎯 Analysis completed successfully!")
        print("=" * 50)

        # Generate report
        print("\n📋 Generating comprehensive report...")
        generate_report(self.results, self.csv_file_path, self.output_folder)

        # Create visualizations  
        print("\n📊 Creating visualizations...")
        create_visualizations(self.results, self.emotion_keywords, self.output_folder)

        # Save results
        print("\n💾 Saving results...")
        save_results(self.results, self.emotion_keywords, self.output_folder)

        print(f"\n🎉 Complete! Successfully analyzed {len(self.results)} videos.")
        print(f"📁 All files saved in: {self.output_folder}")

        return True