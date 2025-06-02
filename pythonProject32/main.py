#!/usr/bin/env python3
"""
Language Emotion Analysis Averaging Project
Main execution file for processing text and image data from analysis folder
"""

import os
import sys
from pathlib import Path

# Add functions folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'functions'))

from text_processor import TextProcessor
from image_processor import ImageProcessor
from file_manager import FileManager


def main():
    """
    Main function to orchestrate the emotion analysis averaging process
    """
    print("Starting Language Emotion Analysis Averaging...")
    
    # Define paths
    input_folder = "analysis_28-05-2025"
    output_folder = f"output_{input_folder}"
    
    # Initialize processors
    file_manager = FileManager()
    text_processor = TextProcessor()
    image_processor = ImageProcessor()
    
    try:
        # Check if input folder exists
        if not file_manager.check_input_folder(input_folder):
            print(f"Error: Input folder '{input_folder}' not found!")
            return
        
        # Create output folder
        file_manager.create_output_folder(output_folder)
        
        # Get all subfolders
        subfolders = file_manager.get_subfolders(input_folder)
        print(f"Found {len(subfolders)} subfolders to process")
        
        if not subfolders:
            print("No subfolders found in the input directory!")
            return
        
        # Process text files
        print("\nProcessing text files...")
        text_data = []
        for subfolder in subfolders:
            text_file_path = file_manager.find_text_file(subfolder)
            if text_file_path:
                data = text_processor.extract_emotion_data(text_file_path)
                if data:
                    text_data.append(data)
                    print(f"Processed text from: {subfolder}")
        
        if text_data:
            averaged_text_data = text_processor.average_emotion_data(text_data)
            output_text_path = os.path.join(output_folder, "averaged_emotion_analysis.txt")
            text_processor.save_averaged_data(averaged_text_data, output_text_path)
            print(f"Averaged text data saved to: {output_text_path}")
        else:
            print("No valid text data found to process!")
        
        # Process image files
        print("\nProcessing image files...")
        image_paths = []
        for subfolder in subfolders:
            image_file_path = file_manager.find_image_file(subfolder)
            if image_file_path:
                image_paths.append(image_file_path)
                print(f"Found image in: {subfolder}")
        
        if image_paths:
            output_image_path = os.path.join(output_folder, "averaged_emotion_graphs.png")
            success = image_processor.create_averaged_image(image_paths, output_image_path)
            if success:
                print(f"Averaged image saved to: {output_image_path}")
            else:
                print("Failed to create averaged image!")
        else:
            print("No valid image files found to process!")
        
        print("\nProcessing completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return


if __name__ == "__main__":
    main()
