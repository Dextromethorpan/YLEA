"""
Text Processor Module
Handles text file processing and emotion analysis data averaging
"""

import re
import os
from typing import List, Dict, Optional, Any
import statistics


class TextProcessor:
    """
    Processes text files containing emotion analysis data and creates averages
    """
    
    def __init__(self):
        """Initialize the TextProcessor"""
        self.emotion_keywords = [
            'anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness',
            'surprise', 'trust', 'positive', 'negative', 'neutral',
            'compound', 'polarity', 'subjectivity', 'confidence'
        ]
    
    def extract_emotion_data(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract emotion analysis data from a text file
        
        Args:
            file_path (str): Path to the text file
            
        Returns:
            Optional[Dict[str, Any]]: Extracted emotion data or None if failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Extract numerical values and their associated emotion labels
            emotion_data = {}
            
            # Look for patterns like "emotion: value" or "emotion = value"
            patterns = [
                r'([a-zA-Z_]+)\s*[:\s=]\s*([-+]?\d*\.?\d+)',
                r'([a-zA-Z_]+)\s*score\s*[:\s=]\s*([-+]?\d*\.?\d+)',
                r'([a-zA-Z_]+)\s*value\s*[:\s=]\s*([-+]?\d*\.?\d+)',
                r'([a-zA-Z_]+)\s*intensity\s*[:\s=]\s*([-+]?\d*\.?\d+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    emotion_name = match[0].lower().strip()
                    try:
                        emotion_value = float(match[1])
                        emotion_data[emotion_name] = emotion_value
                    except ValueError:
                        continue
            
            # Also extract any percentage values
            percentage_pattern = r'([a-zA-Z_]+)\s*[:\s=]\s*([-+]?\d*\.?\d+)%'
            percentage_matches = re.findall(percentage_pattern, content, re.IGNORECASE)
            for match in percentage_matches:
                emotion_name = match[0].lower().strip() + '_percent'
                try:
                    emotion_value = float(match[1])
                    emotion_data[emotion_name] = emotion_value
                except ValueError:
                    continue
            
            # Extract any metadata
            metadata = {
                'file_path': file_path,
                'word_count': len(content.split()),
                'char_count': len(content)
            }
            emotion_data['_metadata'] = metadata
            
            return emotion_data if emotion_data else None
            
        except Exception as e:
            print(f"Error processing text file {file_path}: {str(e)}")
            return None
    
    def average_emotion_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate average values from multiple emotion data dictionaries
        
        Args:
            data_list (List[Dict[str, Any]]): List of emotion data dictionaries
            
        Returns:
            Dict[str, Any]: Averaged emotion data
        """
        if not data_list:
            return {}
        
        # Collect all unique keys (excluding metadata)
        all_keys = set()
        for data in data_list:
            for key in data.keys():
                if key != '_metadata' and isinstance(data[key], (int, float)):
                    all_keys.add(key)
        
        averaged_data = {}
        
        # Calculate averages for each emotion metric
        for key in all_keys:
            values = []
            for data in data_list:
                if key in data and isinstance(data[key], (int, float)):
                    values.append(data[key])
            
            if values:
                averaged_data[key] = {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
        
        # Add summary metadata
        averaged_data['_summary'] = {
            'total_files_processed': len(data_list),
            'total_metrics': len(all_keys),
            'processing_timestamp': self._get_timestamp()
        }
        
        return averaged_data
    
    def save_averaged_data(self, averaged_data: Dict[str, Any], output_path: str) -> bool:
        """
        Save averaged emotion data to a text file
        
        Args:
            averaged_data (Dict[str, Any]): Averaged emotion data
            output_path (str): Path to save the output file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write("AVERAGED LANGUAGE EMOTION ANALYSIS RESULTS\n")
                file.write("=" * 50 + "\n\n")
                
                # Write summary information
                if '_summary' in averaged_data:
                    summary = averaged_data['_summary']
                    file.write(f"Total Files Processed: {summary.get('total_files_processed', 'N/A')}\n")
                    file.write(f"Total Metrics: {summary.get('total_metrics', 'N/A')}\n")
                    file.write(f"Processing Date: {summary.get('processing_timestamp', 'N/A')}\n\n")
                
                # Write emotion metrics
                file.write("EMOTION METRICS AVERAGES\n")
                file.write("-" * 30 + "\n\n")
                
                for key, values in averaged_data.items():
                    if key.startswith('_'):
                        continue
                    
                    if isinstance(values, dict):
                        file.write(f"{key.upper().replace('_', ' ')}:\n")
                        file.write(f"  Mean: {values.get('mean', 0):.4f}\n")
                        file.write(f"  Median: {values.get('median', 0):.4f}\n")
                        file.write(f"  Std Deviation: {values.get('std_dev', 0):.4f}\n")
                        file.write(f"  Range: {values.get('min', 0):.4f} - {values.get('max', 0):.4f}\n")
                        file.write(f"  Sample Count: {values.get('count', 0)}\n\n")
                
                # Write detailed statistics
                file.write("\nDETAILED STATISTICS\n")
                file.write("-" * 20 + "\n")
                
                # Calculate overall statistics
                all_means = [v['mean'] for v in averaged_data.values() 
                           if isinstance(v, dict) and 'mean' in v]
                
                if all_means:
                    file.write(f"Overall Mean of Means: {statistics.mean(all_means):.4f}\n")
                    file.write(f"Overall Std Dev of Means: {statistics.stdev(all_means) if len(all_means) > 1 else 0:.4f}\n")
                
                file.write(f"\nReport generated successfully.\n")
                
            return True
            
        except Exception as e:
            print(f"Error saving averaged data: {str(e)}")
            return False
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp as string
        
        Returns:
            str: Current timestamp
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def validate_text_content(self, file_path: str) -> Dict[str, Any]:
        """
        Validate and analyze text file content
        
        Args:
            file_path (str): Path to text file
            
        Returns:
            Dict[str, Any]: Validation results
        """
        results = {
            'is_valid': False,
            'file_size': 0,
            'line_count': 0,
            'word_count': 0,
            'contains_emotion_data': False,
            'emotion_keywords_found': [],
            'errors': []
        }
        
        try:
            # Check file exists and is readable
            if not os.path.exists(file_path):
                results['errors'].append("File does not exist")
                return results
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            results['file_size'] = len(content)
            results['line_count'] = len(content.splitlines())
            results['word_count'] = len(content.split())
            
            # Check for emotion keywords
            content_lower = content.lower()
            for keyword in self.emotion_keywords:
                if keyword in content_lower:
                    results['emotion_keywords_found'].append(keyword)
            
            # Check for numerical data patterns
            numerical_pattern = r'[-+]?\d*\.?\d+'
            if re.search(numerical_pattern, content):
                results['contains_emotion_data'] = True
            
            results['is_valid'] = (
                results['file_size'] > 0 and 
                results['word_count'] > 0 and
                (results['contains_emotion_data'] or results['emotion_keywords_found'])
            )
            
        except Exception as e:
            results['errors'].append(f"Error reading file: {str(e)}")
        
        return results
