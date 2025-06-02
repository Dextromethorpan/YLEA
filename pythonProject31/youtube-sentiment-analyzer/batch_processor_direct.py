#!/usr/bin/env python3
"""
CSV Batch Processor for YouTube Sentiment Analysis
Direct import method - processes multiple CSV files sequentially
"""

import os
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime
import logging

# Import the analyzer class directly
from Functions.analyzer import YouTubeSentimentAnalyzer


class DirectBatchProcessor:
    """Direct import approach that imports and runs the analyzer directly"""
    
    def __init__(self, csv_directory, output_base_folder=None, delay_between_files=5):
        """
        Initialize the batch processor
        
        Args:
            csv_directory (str): Directory containing CSV files
            output_base_folder (str): Base folder for all outputs (optional)
            delay_between_files (int): Seconds to wait between processing files
        """
        self.csv_directory = Path(csv_directory)
        self.delay_between_files = delay_between_files
        self.results_summary = []
        
        # Set up base output folder
        if output_base_folder is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_base_folder = Path(f"batch_analysis_results_{timestamp}")
        else:
            self.output_base_folder = Path(output_base_folder)
        
        # Create base output folder
        self.output_base_folder.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the batch processor"""
        log_filename = self.output_base_folder / f"batch_processor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Batch processor initialized. Log file: {log_filename}")
        self.logger.info(f"Base output folder: {self.output_base_folder}")
    
    def find_csv_files(self):
        """Find all CSV files in the specified directory"""
        if not self.csv_directory.exists():
            self.logger.error(f"Directory does not exist: {self.csv_directory}")
            return []
        
        csv_files = list(self.csv_directory.glob("*.csv"))
        self.logger.info(f"Found {len(csv_files)} CSV files in {self.csv_directory}")
        
        for csv_file in csv_files:
            self.logger.info(f"  - {csv_file.name}")
            
        return sorted(csv_files)  # Sort for consistent processing order
    
    def process_single_csv(self, csv_file):
        """
        Process a single CSV file using direct import
        
        Args:
            csv_file (Path): Path to the CSV file
            
        Returns:
            dict: Processing results
        """
        self.logger.info(f"Processing: {csv_file.name}")
        start_time = time.time()
        
        try:
            # Create individual output folder for this CSV
            csv_name = csv_file.stem  # filename without extension
            individual_output_folder = self.output_base_folder / f"results_{csv_name}"
            
            # Create analyzer instance
            analyzer = YouTubeSentimentAnalyzer(
                csv_file_path=str(csv_file),
                output_folder=str(individual_output_folder)
            )
            
            # Run analysis
            success = analyzer.run_analysis()
            
            end_time = time.time()
            duration = end_time - start_time
            
            if success:
                self.logger.info(f"✅ Successfully processed {csv_file.name} in {duration:.1f}s")
                self.logger.info(f"   📊 Videos analyzed: {len(analyzer.results)}")
                self.logger.info(f"   📁 Results saved in: {individual_output_folder}")
                
                return {
                    'file': csv_file.name,
                    'status': 'success',
                    'duration': duration,
                    'videos_processed': len(analyzer.results),
                    'output_folder': str(individual_output_folder),
                    'analyzer_results': analyzer.results
                }
            else:
                self.logger.error(f"❌ Failed to process {csv_file.name}")
                return {
                    'file': csv_file.name,
                    'status': 'failed',
                    'duration': duration,
                    'videos_processed': 0,
                    'output_folder': str(individual_output_folder),
                    'error': 'Analysis failed'
                }
                
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            self.logger.error(f"💥 Exception processing {csv_file.name}: {str(e)}")
            return {
                'file': csv_file.name,
                'status': 'error',
                'duration': duration,
                'videos_processed': 0,
                'output_folder': None,
                'error': str(e)
            }
    
    def process_all_csv_files(self):
        """Process all CSV files in the directory sequentially"""
        csv_files = self.find_csv_files()
        
        if not csv_files:
            self.logger.warning("No CSV files found to process")
            return False
        
        self.logger.info(f"Starting batch processing of {len(csv_files)} files")
        self.logger.info(f"Delay between files: {self.delay_between_files} seconds")
        self.logger.info(f"Base output folder: {self.output_base_folder}")
        
        # Process each file
        total_start_time = time.time()
        
        for i, csv_file in enumerate(csv_files, 1):
            self.logger.info(f"📊 Processing file {i}/{len(csv_files)}: {csv_file.name}")
            
            result = self.process_single_csv(csv_file)
            self.results_summary.append(result)
            
            # Add delay between files (except for the last one)
            if i < len(csv_files) and self.delay_between_files > 0:
                self.logger.info(f"⏳ Waiting {self.delay_between_files} seconds before next file...")
                time.sleep(self.delay_between_files)
        
        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        
        # Generate summary report
        self.generate_summary_report(total_duration)
        return True
    
    def generate_summary_report(self, total_duration):
        """Generate a summary report of all processing results"""
        if not self.results_summary:
            return
        
        self.logger.info("=" * 70)
        self.logger.info("BATCH PROCESSING SUMMARY REPORT")
        self.logger.info("=" * 70)
        
        total_files = len(self.results_summary)
        successful = len([r for r in self.results_summary if r['status'] == 'success'])
        failed = len([r for r in self.results_summary if r['status'] == 'failed'])
        errors = len([r for r in self.results_summary if r['status'] == 'error'])
        
        total_videos = sum(r.get('videos_processed', 0) for r in self.results_summary)
        avg_duration = sum(r['duration'] for r in self.results_summary) / total_files if total_files > 0 else 0
        
        self.logger.info(f"Total Files Processed: {total_files}")
        self.logger.info(f"Successful: {successful}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Errors: {errors}")
        self.logger.info(f"Success Rate: {(successful/total_files*100):.1f}%")
        self.logger.info(f"Total Videos Analyzed: {total_videos}")
        self.logger.info(f"Total Processing Time: {total_duration/3600:.1f} hours")
        self.logger.info(f"Average Time per File: {avg_duration:.1f} seconds")
        
        # List successful files
        successful_files = [r for r in self.results_summary if r['status'] == 'success']
        if successful_files:
            self.logger.info(f"\nSuccessful Files ({len(successful_files)}):")
            for result in successful_files:
                self.logger.info(f"  ✅ {result['file']}: {result['videos_processed']} videos processed")
        
        # List failed files
        failed_files = [r for r in self.results_summary if r['status'] != 'success']
        if failed_files:
            self.logger.info(f"\nFailed Files ({len(failed_files)}):")
            for result in failed_files:
                error_msg = result.get('error', 'Unknown error')[:100]
                self.logger.info(f"  ❌ {result['file']}: {result['status']} - {error_msg}")
        
        # Save detailed summary to CSV
        self.save_summary_to_csv()
        
        self.logger.info(f"\n📁 All results saved in: {self.output_base_folder}")
    
    def save_summary_to_csv(self):
        """Save batch processing summary to CSV"""
        import pandas as pd
        
        summary_data = []
        for result in self.results_summary:
            summary_data.append({
                'file_name': result['file'],
                'status': result['status'],
                'duration_seconds': round(result['duration'], 1),
                'videos_processed': result.get('videos_processed', 0),
                'output_folder': result.get('output_folder', ''),
                'error': result.get('error', '')
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_filename = self.output_base_folder / f"batch_processing_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        summary_df.to_csv(summary_filename, index=False)
        
        self.logger.info(f"📄 Summary saved as: {summary_filename}")


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Batch process multiple CSV files through YouTube sentiment analyzer (Direct Import Method)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_processor.py /path/to/csv/files
  python batch_processor.py ./csv_files --delay 10
  python batch_processor.py ./csv_files --output ./batch_results --delay 5

This script uses the direct import method for better performance and simpler debugging.
        """
    )
    
    parser.add_argument(
        'csv_directory',
        help='Directory containing CSV files to process'
    )
    
    parser.add_argument(
        '--output',
        help='Base output directory for all results (optional - will auto-generate if not provided)'
    )
    
    parser.add_argument(
        '--delay',
        type=int,
        default=5,
        help='Seconds to wait between processing files (default: 5)'
    )
    
    args = parser.parse_args()
    
    # Validate CSV directory
    if not os.path.exists(args.csv_directory):
        print(f"❌ Error: Directory '{args.csv_directory}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(args.csv_directory):
        print(f"❌ Error: '{args.csv_directory}' is not a directory.")
        sys.exit(1)
    
    # Create and run batch processor
    processor = DirectBatchProcessor(
        csv_directory=args.csv_directory,
        output_base_folder=args.output,
        delay_between_files=args.delay
    )
    
    success = processor.process_all_csv_files()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    print("CSV Batch Processor for YouTube Sentiment Analysis")
    print("Direct Import Method - Enhanced Performance")
    print("=" * 60)
    print("🚀 Usage:")
    print("   python batch_processor.py /path/to/csv/directory")
    print("   python batch_processor.py ./csv_files --delay 10")
    print("   python batch_processor.py ./csv_files --output ./results")
    print("=" * 60)
    
    main()