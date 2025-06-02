"""
Image Processor Module
Handles image processing and averaging of 9-graph emotion analysis visualizations
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional
import os


class ImageProcessor:
    """
    Processes images containing 9 emotion analysis graphs and creates averaged visualizations
    """
    
    def __init__(self):
        """Initialize the ImageProcessor"""
        self.grid_size = (3, 3)  # 3x3 grid for 9 graphs
        self.min_image_size = (300, 300)
        self.default_output_size = (1200, 1200)
    
    def load_and_validate_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load and validate an image file
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Optional[np.ndarray]: Loaded image as numpy array or None if failed
        """
        try:
            # Load image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                # Try with PIL if OpenCV fails
                pil_image = Image.open(image_path)
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            if image is None:
                print(f"Failed to load image: {image_path}")
                return None
            
            # Basic validation
            height, width = image.shape[:2]
            if height < self.min_image_size[0] or width < self.min_image_size[1]:
                print(f"Image too small: {image_path} ({width}x{height})")
                return None
            
            return image
            
        except Exception as e:
            print(f"Error loading image {image_path}: {str(e)}")
            return None
    
    def detect_graph_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect the 9 graph regions in the image
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            List[Tuple[int, int, int, int]]: List of (x, y, width, height) for each graph region
        """
        height, width = image.shape[:2]
        
        # Assume 3x3 grid layout
        region_width = width // 3
        region_height = height // 3
        
        regions = []
        for row in range(3):
            for col in range(3):
                x = col * region_width
                y = row * region_height
                regions.append((x, y, region_width, region_height))
        
        return regions
    
    def extract_graph_features(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> dict:
        """
        Extract features from a graph region
        
        Args:
            image (np.ndarray): Source image
            region (Tuple[int, int, int, int]): Region coordinates (x, y, width, height)
            
        Returns:
            dict: Extracted features
        """
        x, y, w, h = region
        roi = image[y:y+h, x:x+w]
        
        # Extract color statistics
        mean_colors = np.mean(roi, axis=(0, 1))
        std_colors = np.std(roi, axis=(0, 1))
        
        # Convert to grayscale for intensity analysis
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Extract intensity features
        mean_intensity = np.mean(gray_roi)
        std_intensity = np.std(gray_roi)
        
        # Edge detection for graph structure
        edges = cv2.Canny(gray_roi, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Histogram features
        hist = cv2.calcHist([gray_roi], [0], None, [256], [0, 256])
        hist_flat = hist.flatten()
        
        # Calculate weighted standard deviation manually for compatibility
        indices = np.arange(256)
        weights_sum = np.sum(hist_flat)
        if weights_sum > 0:
            weighted_mean = np.sum(indices * hist_flat) / weights_sum
            weighted_variance = np.sum(hist_flat * (indices - weighted_mean) ** 2) / weights_sum
            hist_spread = np.sqrt(weighted_variance)
        else:
            hist_spread = 0.0
        
        hist_features = {
            'peak_intensity': np.argmax(hist),
            'hist_spread': hist_spread
        }
        
        return {
            'region': region,
            'mean_colors': mean_colors,
            'std_colors': std_colors,
            'mean_intensity': mean_intensity,
            'std_intensity': std_intensity,
            'edge_density': edge_density,
            'histogram': hist_features,
            'roi_shape': roi.shape
        }
    
    def average_graph_features(self, features_list: List[dict]) -> dict:
        """
        Average features from multiple graphs in the same position
        
        Args:
            features_list (List[dict]): List of feature dictionaries
            
        Returns:
            dict: Averaged features
        """
        if not features_list:
            return {}
        
        # Average numerical features
        avg_features = {
            'mean_colors': np.mean([f['mean_colors'] for f in features_list], axis=0),
            'std_colors': np.mean([f['std_colors'] for f in features_list], axis=0),
            'mean_intensity': np.mean([f['mean_intensity'] for f in features_list]),
            'std_intensity': np.mean([f['std_intensity'] for f in features_list]),
            'edge_density': np.mean([f['edge_density'] for f in features_list]),
            'region': features_list[0]['region'],  # Use first region as reference
            'count': len(features_list)
        }
        
        # Average histogram features
        avg_features['histogram'] = {
            'peak_intensity': np.mean([f['histogram']['peak_intensity'] for f in features_list]),
            'hist_spread': np.mean([f['histogram']['hist_spread'] for f in features_list])
        }
        
        return avg_features
    
    def generate_averaged_graph(self, avg_features: dict, size: Tuple[int, int]) -> np.ndarray:
        """
        Generate a graph visualization from averaged features
        
        Args:
            avg_features (dict): Averaged features
            size (Tuple[int, int]): Output size (width, height)
            
        Returns:
            np.ndarray: Generated graph image
        """
        width, height = size
        
        # Create base image with averaged background color
        bg_color = avg_features['mean_colors'].astype(np.uint8)
        graph_img = np.full((height, width, 3), bg_color, dtype=np.uint8)
        
        # Add some visualization based on features
        center_x, center_y = width // 2, height // 2
        
        # Draw intensity-based circle
        intensity_radius = int((avg_features['mean_intensity'] / 255.0) * min(width, height) // 4)
        cv2.circle(graph_img, (center_x, center_y), intensity_radius, 
                  (255, 255, 255), thickness=2)
        
        # Add edge density visualization as lines
        edge_density = avg_features['edge_density']
        num_lines = int(edge_density * 20)  # Scale to reasonable number
        
        for i in range(num_lines):
            angle = (2 * np.pi * i) / num_lines
            x1 = int(center_x + intensity_radius * np.cos(angle))
            y1 = int(center_y + intensity_radius * np.sin(angle))
            x2 = int(center_x + (intensity_radius + 20) * np.cos(angle))
            y2 = int(center_y + (intensity_radius + 20) * np.sin(angle))
            cv2.line(graph_img, (x1, y1), (x2, y2), (0, 255, 0), thickness=1)
        
        # Add text information
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        text_color = (0, 0, 0)
        
        # Add intensity value
        intensity_text = f"Avg: {avg_features['mean_intensity']:.1f}"
        cv2.putText(graph_img, intensity_text, (5, 15), font, font_scale, text_color, 1)
        
        # Add sample count
        count_text = f"N: {avg_features['count']}"
        cv2.putText(graph_img, count_text, (5, height - 5), font, font_scale, text_color, 1)
        
        return graph_img
    
    def create_averaged_image(self, image_paths: List[str], output_path: str) -> bool:
        """
        Create an averaged image from multiple 9-graph emotion analysis images
        
        Args:
            image_paths (List[str]): List of paths to input images
            output_path (str): Path to save the averaged image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not image_paths:
                print("No image paths provided")
                return False
            
            print(f"Processing {len(image_paths)} images...")
            
            # Load and validate all images
            valid_images = []
            for img_path in image_paths:
                img = self.load_and_validate_image(img_path)
                if img is not None:
                    valid_images.append(img)
                else:
                    print(f"Skipping invalid image: {img_path}")
            
            if not valid_images:
                print("No valid images found")
                return False
            
            print(f"Successfully loaded {len(valid_images)} images")
            
            # Resize all images to same size for consistency
            target_size = self.default_output_size
            resized_images = []
            for img in valid_images:
                resized = cv2.resize(img, target_size)
                resized_images.append(resized)
            
            # Extract features for each graph position across all images
            all_graph_features = [[] for _ in range(9)]  # 9 positions in 3x3 grid
            
            for img in resized_images:
                regions = self.detect_graph_regions(img)
                for i, region in enumerate(regions):
                    features = self.extract_graph_features(img, region)
                    all_graph_features[i].append(features)
            
            # Average features for each graph position
            averaged_graph_features = []
            for i in range(9):
                if all_graph_features[i]:
                    avg_features = self.average_graph_features(all_graph_features[i])
                    averaged_graph_features.append(avg_features)
                else:
                    print(f"No features found for graph position {i}")
                    return False
            
            # Create the final averaged image
            final_image = self.create_final_averaged_image(averaged_graph_features, target_size)
            
            # Save the result
            success = cv2.imwrite(output_path, final_image)
            if success:
                print(f"Averaged image saved successfully: {output_path}")
                return True
            else:
                print(f"Failed to save image: {output_path}")
                return False
            
        except Exception as e:
            print(f"Error creating averaged image: {str(e)}")
            return False
    
    def create_final_averaged_image(self, graph_features: List[dict], image_size: Tuple[int, int]) -> np.ndarray:
        """
        Create the final averaged image with 9 graphs arranged in a 3x3 grid
        
        Args:
            graph_features (List[dict]): List of averaged features for each graph position
            image_size (Tuple[int, int]): Target image size (width, height)
            
        Returns:
            np.ndarray: Final averaged image
        """
        width, height = image_size
        final_image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Calculate individual graph size
        graph_width = width // 3
        graph_height = height // 3
        
        # Generate each graph and place it in the grid
        for i, features in enumerate(graph_features):
            row = i // 3
            col = i % 3
            
            # Generate individual graph
            graph_img = self.generate_averaged_graph(features, (graph_width, graph_height))
            
            # Calculate position in final image
            x_start = col * graph_width
            y_start = row * graph_height
            x_end = x_start + graph_width
            y_end = y_start + graph_height
            
            # Place graph in final image
            final_image[y_start:y_end, x_start:x_end] = graph_img
            
            # Add grid lines for separation
            if col < 2:  # Vertical lines
                cv2.line(final_image, (x_end, 0), (x_end, height), (128, 128, 128), 2)
            if row < 2:  # Horizontal lines
                cv2.line(final_image, (0, y_end), (width, y_end), (128, 128, 128), 2)
        
        # Add title
        self.add_title_to_image(final_image, "Averaged Emotion Analysis Graphs")
        
        return final_image
    
    def add_title_to_image(self, image: np.ndarray, title: str) -> None:
        """
        Add a title to the image
        
        Args:
            image (np.ndarray): Image to add title to
            title (str): Title text
        """
        try:
            # Convert to PIL for better text rendering
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_image)
            
            # Try to load a font, fallback to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position
            text_width = draw.textlength(title, font=font)
            x = (pil_image.width - text_width) // 2
            y = 10
            
            # Add text with background
            draw.rectangle([x-5, y-5, x+text_width+5, y+30], fill=(255, 255, 255, 200))
            draw.text((x, y), title, fill=(0, 0, 0), font=font)
            
            # Convert back to OpenCV format
            result = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            image[:] = result
            
        except Exception as e:
            print(f"Error adding title: {str(e)}")
            # Fallback to OpenCV text
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image, title, (50, 30), font, 0.8, (255, 255, 255), 2)
    
    def validate_image_structure(self, image_path: str) -> dict:
        """
        Validate that an image contains the expected 9-graph structure
        
        Args:
            image_path (str): Path to the image
            
        Returns:
            dict: Validation results
        """
        results = {
            'is_valid': False,
            'image_size': (0, 0),
            'detected_regions': 0,
            'has_graphs': False,
            'errors': []
        }
        
        try:
            image = self.load_and_validate_image(image_path)
            if image is None:
                results['errors'].append("Could not load image")
                return results
            
            height, width = image.shape[:2]
            results['image_size'] = (width, height)
            
            # Detect graph regions
            regions = self.detect_graph_regions(image)
            results['detected_regions'] = len(regions)
            
            # Check if regions contain graph-like content
            graph_count = 0
            for region in regions:
                features = self.extract_graph_features(image, region)
                # Simple heuristic: if edge density is above threshold, likely contains a graph
                if features['edge_density'] > 0.01:  # Adjust threshold as needed
                    graph_count += 1
            
            results['has_graphs'] = graph_count >= 6  # At least 6 out of 9 regions should have graph content
            results['is_valid'] = (
                results['detected_regions'] == 9 and 
                results['has_graphs'] and 
                width >= self.min_image_size[0] and 
                height >= self.min_image_size[1]
            )
            
        except Exception as e:
            results['errors'].append(f"Error validating image: {str(e)}")
        
        return results