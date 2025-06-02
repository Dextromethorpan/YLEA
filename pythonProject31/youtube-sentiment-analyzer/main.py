"""
YouTube Sentiment Analyzer - Main Entry Point
Modular version with functions organized in separate modules
"""

import argparse
import sys
import os

# Import the main analyzer class from Functions module
from Functions.analyzer import YouTubeSentimentAnalyzer


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Analyze sentiment and emotions in YouTube videos from a CSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py my_videos.csv
  python main.py /path/to/videos.csv
  python main.py my_videos.csv --output /path/to/output/folder

The CSV file should contain a column with YouTube video IDs or URLs.
Supported column names: video_id, url, video_url, youtube_url, link
        """
    )

    parser.add_argument(
        'csv_file',
        help='Path to the CSV file containing YouTube video IDs or URLs'
    )

    parser.add_argument(
        '--output',
        help='Path to output folder (optional - will auto-generate if not provided)'
    )

    args = parser.parse_args()

    # Check if file exists
    if not os.path.exists(args.csv_file):
        print(f"❌ Error: File '{args.csv_file}' does not exist.")
        sys.exit(1)

    # Create analyzer and run
    analyzer = YouTubeSentimentAnalyzer(args.csv_file, args.output)
    success = analyzer.run_analysis()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    print("YouTube Sentiment Analyzer - Modular Version")
    print("=" * 45)
    print("📋 Required packages:")
    print("   pip install pandas matplotlib seaborn textblob youtube-transcript-api numpy")
    print("   python -m textblob.corpora.download")
    print("\n🚀 Usage:")
    print("   python main.py your_file.csv")
    print("   python main.py your_file.csv --output ./results")
    print("=" * 45)

    # Run main function
    main()