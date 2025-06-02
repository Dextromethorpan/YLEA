# Language Emotion Analysis Averaging Project

## Overview
This PyCharm project processes language emotion analysis data from text files and images containing 9-graph visualizations. It creates averaged results from multiple analysis files organized in subfolders, producing consolidated text and image outputs.

## Project Structure
```
emotion_analysis_project/
├── main.py                    # Main execution file
├── requirements.txt           # Required Python packages
├── README.md                 # This documentation file
├── functions/                # Custom function modules
│   ├── file_manager.py       # File and folder operations
│   ├── text_processor.py     # Text analysis and averaging
│   └── image_processor.py    # Image processing and averaging
├── analysis_28-05-2025/      # Input folder (user-provided)
│   ├── subfolder1/
│   │   ├── analysis.txt      # Emotion analysis text file
│   │   └── graphs.png        # 9-graph image file
│   ├── subfolder2/
│   │   ├── analysis.txt
│   │   └── graphs.png
│   └── ...
└── output/                   # Generated output folder
    ├── averaged_emotion_analysis.txt
    └── averaged_emotion_graphs.png
```

## Installation

### Prerequisites
- Python 3.8 or higher
- PyCharm IDE (recommended)

### Setup Instructions
1. Clone or download this project to your local machine
2. Open the project in PyCharm
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure your input folder `analysis_28-05-2025` is placed in the project root directory

## Input Requirements

### Folder Structure
- The input folder `analysis_28-05-2025` should contain multiple subfolders
- Each subfolder must contain:
  - **One text file** with emotion analysis data (`.txt`, `.md`, or `.text` format)
  - **One image file** with 9 graphs arranged in a 3×3 grid (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, or `.gif`)

### Text File Format
Text files should contain emotion analysis data with patterns like:
- `emotion_name: value`
- `emotion_name = value`
- `emotion_name score: value`
- Supported emotions: anger, joy, sadness, fear, surprise, trust, etc.
- Numerical values and percentages are automatically extracted

### Image File Format
- Images should contain 9 separate graphs arranged in a 3×3 grid
- Each graph represents different emotion analysis visualizations
- Supported formats: PNG, JPG, JPEG, BMP, TIFF, GIF

## Usage

### Running the Project
1. Place your `analysis_28-05-2025` folder in the project root
2. Run the main script:
   ```bash
   python main.py
   ```
3. The program will:
   - Scan all subfolders for text and image files
   - Process and average the emotion data from text files  
   - Process and average the 9-graph images
   - Generate output files in the `output/` folder

### Output Files
1. **`averaged_emotion_analysis.txt`**: Contains statistical averages of all emotion metrics including:
   - Mean, median, standard deviation for each emotion
   - Min/max ranges and sample counts
   - Overall summary statistics

2. **`averaged_emotion_graphs.png`**: A composite image showing averaged visualizations from all input images, maintaining the 3×3 grid layout

## Functions Documentation

### FileManager (`functions/file_manager.py`)
Handles all file and folder operations:
- **`check_input_folder()`**: Validates input folder existence
- **`create_output_folder()`**: Creates output directory structure
- **`get_subfolders()`**: Retrieves all subfolders from input directory
- **`find_text_file()`**: Locates text files in subfolders
- **`find_image_file()`**: Locates image files in subfolders
- **`validate_file_structure()`**: Validates expected file organization

### TextProcessor (`functions/text_processor.py`)
Processes emotion analysis text data:
- **`extract_emotion_data()`**: Extracts numerical emotion values from text files
- **`average_emotion_data()`**: Calculates statistical averages across multiple files
- **`save_averaged_data()`**: Saves averaged results to formatted text file
- **`validate_text_content()`**: Validates text file content and structure

### ImageProcessor (`functions/image_processor.py`)
Handles image processing and averaging:
- **`load_and_validate_image()`**: Loads and validates image files
- **`detect_graph_regions()`**: Identifies 9 graph regions in 3×3 grid layout  
- **`extract_graph_features()`**: Extracts visual features from each graph region
- **`average_graph_features()`**: Averages features across multiple images
- **`create_averaged_image()`**: Generates final averaged visualization
- **`validate_image_structure()`**: Validates 9-graph image structure

## Features

### Text Processing Features
- Automatic extraction of emotion metrics from various text formats
- Statistical analysis including mean, median, standard deviation
- Support for percentage values and confidence scores
- Robust parsing with multiple pattern recognition
- Comprehensive error handling and validation

### Image Processing Features
- 3×3 grid detection and region extraction
- Color and intensity feature analysis
- Edge density calculation for graph structure detection
- Visual averaging with feature-based reconstruction
- Automatic image resizing and grid alignment
- Title and metadata overlay on output images

### Error Handling
- Comprehensive validation of input files and folders
- Graceful handling of missing or corrupted files
- Detailed error reporting and logging
- Fallback mechanisms for various file format issues

## Troubleshooting

### Common Issues
1. **"Input folder not found"**: Ensure `analysis_28-05-2025` folder exists in project root
2. **"No valid files found"**: Check that subfolders contain both text and image files
3. **Image processing errors**: Verify images are readable and contain 9-graph layout
4. **Text parsing issues**: Ensure text files contain recognizable emotion data patterns

### Dependencies Issues
If you encounter import errors:
```bash
pip install --upgrade -r requirements.txt
```

## Technical Requirements
- **Python**: 3.8+
- **Memory**: Minimum 4GB RAM (8GB+ recommended for large datasets)
- **Storage**: Adequate space for input images and output files
- **Libraries**: OpenCV, PIL, NumPy, Matplotlib, Pandas

## License
This project is designed for academic and research purposes. Please ensure compliance with relevant data usage policies when processing emotion analysis data.

## Support
For issues or questions about this project, please check:
1. Input file format requirements
2. Folder structure organization  
3. Required dependencies installation
4. Python version compatibility

---
*Generated for Language Emotion Analysis Averaging Project*