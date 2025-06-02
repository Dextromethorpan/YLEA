# YouTube Sentiment Analyzer - Modular Version

A comprehensive Python application for analyzing sentiment and emotions in YouTube videos using transcripts. The application is now modularized with functions organized in separate modules for better maintainability and reusability.

## 🏗️ Project Structure

```
youtube-sentiment-analyzer/
├── main.py                     # Main entry point
├── batch_processor.py          # Batch processing script
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── Functions/                 # Core functionality modules
│   ├── __init__.py           # Package initialization
│   ├── analyzer.py           # Main analyzer class
│   ├── sentiment_analysis.py # Sentiment & emotion analysis
│   ├── video_processing.py   # Video & transcript processing
│   ├── csv_processing.py     # CSV file handling
│   ├── visualization.py      # Chart and graph generation
│   └── reporting.py          # Report generation & file saving
├── csv_files/                # Input CSV files directory
│   ├── video_list_1.csv
│   ├── video_list_2.csv
│   └── video_list_3.csv
└── batch_analysis_results_*/  # Generated output folders
    ├── results_video_list_1/
    ├── results_video_list_2/
    └── batch_processing_summary.csv
```

## 📋 Features

### Core Analysis
- **Sentiment Analysis**: Uses TextBlob to analyze positive, negative, and neutral sentiments
- **Emotion Detection**: Identifies 8 different emotions (joy, anger, fear, sadness, surprise, disgust, trust, anticipation)
- **Segment Analysis**: Breaks videos into 30-second segments for detailed timeline analysis
- **Empty CSV Detection**: Automatically detects and handles empty or invalid CSV files

### Visualization
- Overall sentiment distribution (pie charts)
- Sentiment polarity distribution (histograms)
- Average emotion scores (bar charts)
- Video length vs sentiment correlation (scatter plots)
- Emotion intensity heatmaps
- Sentiment timeline analysis
- Comprehensive multi-panel dashboards

### Output & Reporting
- **Organized Output Folders**: All results saved in structured directories
- **Comprehensive Reports**: Detailed text reports with statistics and insights
- **CSV Export**: Segment-level and video-level data export
- **High-Quality Visualizations**: Publication-ready charts and graphs

### Batch Processing
- **Sequential Processing**: Process multiple CSV files automatically
- **Progress Tracking**: Real-time progress monitoring with logs
- **Error Handling**: Continues processing even if individual files fail
- **Configurable Delays**: Respectful API usage with adjustable delays
- **Summary Reports**: Batch processing summaries and success rates

## 🚀 Installation

1. **Clone or download the project files**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Download TextBlob corpora:**
```bash
python -m textblob.corpora.download
```

## 💡 Usage

### Single CSV Analysis
```bash
# Basic usage
python main.py your_videos.csv

# Specify output folder
python main.py your_videos.csv --output ./my_results
```

### Batch Processing (Recommended)
```bash
# Process all CSV files in a directory
python batch_processor.py ./csv_files

# With custom delay and output folder
python batch_processor.py ./csv_files --delay 10 --output ./batch_results
```

## 📊 CSV File Format

Your CSV files should contain YouTube video IDs or URLs. Supported column names:
- `video_id`
- `url` 
- `video_url`
- `youtube_url`
- `link`
- `Video ID`
- `URL`
- `Video URL`

**Example CSV:**
```csv
video_id,title
dQw4w9WgXcQ,Rick Astley - Never Gonna Give You Up
jNQXAC9IVRw,Me at the zoo
```

## 📁 Output Structure

Each analysis generates:

```
analysis_results_[csv_name]_[timestamp]/
├── youtube_sentiment_analysis_[timestamp].png    # Visualization dashboard
├── sentiment_analysis_report_[timestamp].txt     # Comprehensive text report
├── sentiment_segments_[timestamp].csv            # Detailed segment analysis
└── overall_sentiment_results_[timestamp].csv     # Video-level summary
```

For batch processing:
```
batch_analysis_results_[timestamp]/
├── results_file1/                               # Individual CSV results
├── results_file2/
├── batch_processor_[timestamp].log              # Processing log
└── batch_processing_summary_[timestamp].csv     # Batch summary
```

## 🔧 Module Architecture

### Functions/analyzer.py
Main analyzer class that orchestrates the entire analysis pipeline.

### Functions/sentiment_analysis.py
- TextBlob-based sentiment analysis
- Emotion keyword matching
- Configurable emotion dictionaries

### Functions/video_processing.py
- YouTube video ID extraction
- Transcript retrieval via YouTube API
- Video segmentation and processing

### Functions/csv_processing.py
- CSV file validation and loading
- Empty file detection
- Data preprocessing and cleaning

### Functions/visualization.py
- Multi-panel dashboard creation
- Various chart types (pie, bar, scatter, heatmap)
- Publication-quality output

### Functions/reporting.py
- Comprehensive text report generation
- CSV export functionality
- Statistics calculation and summary

## 🛠️ Customization

### Adding New Emotions
Edit `Functions/sentiment_analysis.py`:
```python
EMOTION_KEYWORDS = {
    'your_emotion': ['keyword1', 'keyword2', 'keyword3'],
    # ... existing emotions
}
```

### Adjusting Segment Size
Modify `Functions/video_processing.py`:
```python
segment_size = 60  # Change from 30 to 60 seconds
```

### Custom Output Formats
Extend `Functions/reporting.py` to add new export formats.

## ⚠️ Important Notes

- **YouTube API Limits**: The application includes respectful delays to avoid rate limiting
- **Transcript Availability**: Only works with videos that have available transcripts
- **Processing Time**: Large batches may take considerable time due to API calls
- **Memory Usage**: Large CSV files with many videos may require substantial memory

## 🔍 Troubleshooting

### Common Issues:

1. **"No transcript available"**: Video doesn't have captions/transcript
2. **CSV format errors**: Check column names match supported formats
3. **Empty results**: Verify video IDs/URLs are valid
4. **Memory errors**: Process smaller batches or individual files

### Debug Mode:
The application includes comprehensive logging. Check the generated `.log` files for detailed processing information.

## 📈 Performance Tips

1. **Batch Processing**: Use `batch_processor.py` for multiple files
2. **Delay Configuration**: Adjust `--delay` parameter based on your needs
3. **Output Organization**: Results are automatically organized in timestamped folders
4. **Error Recovery**: Batch processor continues even if individual files fail

## 🤝 Contributing

The modular architecture makes it easy to extend functionality:
- Add new analysis methods in respective modules
- Extend visualization options in `visualization.py`
- Add new export formats in `reporting.py`
- Enhance CSV processing in `csv_processing.py`

## 📜 License

This project is provided as-is for educational and research purposes.