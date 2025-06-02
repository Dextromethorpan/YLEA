"""
File Manager Module
Handles all file and folder operations for the emotion analysis project
"""

import os
from pathlib import Path
from typing import List, Optional


class FileManager:
    """
    Manages file and folder operations for the emotion analysis averaging project
    """
    
    def __init__(self):
        """Initialize the FileManager"""
        self.supported_image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
        self.supported_text_extensions = ['.txt', '.md', '.text']
    
    def check_input_folder(self, folder_path: str) -> bool:
        """
        Check if the input folder exists
        
        Args:
            folder_path (str): Path to the input folder
            
        Returns:
            bool: True if folder exists, False otherwise
        """
        return os.path.exists(folder_path) and os.path.isdir(folder_path)
    
    def create_output_folder(self, folder_path: str) -> bool:
        """
        Create output folder if it doesn't exist
        
        Args:
            folder_path (str): Path to the output folder
            
        Returns:
            bool: True if folder was created or already exists, False otherwise
        """
        try:
            os.makedirs(folder_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating output folder: {str(e)}")
            return False
    
    def get_subfolders(self, parent_folder: str) -> List[str]:
        """
        Get all subfolders within the parent folder
        
        Args:
            parent_folder (str): Path to the parent folder
            
        Returns:
            List[str]: List of subfolder paths
        """
        subfolders = []
        try:
            for item in os.listdir(parent_folder):
                item_path = os.path.join(parent_folder, item)
                if os.path.isdir(item_path):
                    subfolders.append(item_path)
        except Exception as e:
            print(f"Error getting subfolders: {str(e)}")
        
        return sorted(subfolders)
    
    def find_text_file(self, folder_path: str) -> Optional[str]:
        """
        Find the first text file in the given folder
        
        Args:
            folder_path (str): Path to search for text files
            
        Returns:
            Optional[str]: Path to the text file if found, None otherwise
        """
        try:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    file_ext = Path(file).suffix.lower()
                    if file_ext in self.supported_text_extensions:
                        return file_path
        except Exception as e:
            print(f"Error finding text file in {folder_path}: {str(e)}")
        
        return None
    
    def find_image_file(self, folder_path: str) -> Optional[str]:
        """
        Find the first image file in the given folder
        
        Args:
            folder_path (str): Path to search for image files
            
        Returns:
            Optional[str]: Path to the image file if found, None otherwise
        """
        try:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    file_ext = Path(file).suffix.lower()
                    if file_ext in self.supported_image_extensions:
                        return file_path
        except Exception as e:
            print(f"Error finding image file in {folder_path}: {str(e)}")
        
        return None
    
    def get_all_files_by_type(self, folder_path: str, file_type: str) -> List[str]:
        """
        Get all files of a specific type from folder and subfolders
        
        Args:
            folder_path (str): Root folder path
            file_type (str): 'text' or 'image'
            
        Returns:
            List[str]: List of file paths
        """
        files = []
        
        if file_type == 'text':
            extensions = self.supported_text_extensions
        elif file_type == 'image':
            extensions = self.supported_image_extensions
        else:
            return files
        
        try:
            for root, dirs, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_ext = Path(filename).suffix.lower()
                    if file_ext in extensions:
                        files.append(os.path.join(root, filename))
        except Exception as e:
            print(f"Error getting {file_type} files: {str(e)}")
        
        return files
    
    def validate_file_structure(self, folder_path: str) -> dict:
        """
        Validate the expected file structure
        
        Args:
            folder_path (str): Path to validate
            
        Returns:
            dict: Validation results with statistics
        """
        results = {
            'valid_subfolders': 0,
            'subfolders_with_text': 0,
            'subfolders_with_images': 0,
            'subfolders_with_both': 0,
            'total_subfolders': 0,
            'issues': []
        }
        
        subfolders = self.get_subfolders(folder_path)
        results['total_subfolders'] = len(subfolders)
        
        for subfolder in subfolders:
            has_text = self.find_text_file(subfolder) is not None
            has_image = self.find_image_file(subfolder) is not None
            
            if has_text:
                results['subfolders_with_text'] += 1
            if has_image:
                results['subfolders_with_images'] += 1
            if has_text and has_image:
                results['subfolders_with_both'] += 1
            if has_text or has_image:
                results['valid_subfolders'] += 1
            
            if not has_text and not has_image:
                results['issues'].append(f"No valid files found in: {subfolder}")
        
        return results
