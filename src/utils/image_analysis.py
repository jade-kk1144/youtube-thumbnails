# src/utils/image_analysis.py

import numpy as np
from PIL import Image
# import face_recognition
import easyocr
from sklearn.cluster import KMeans
from typing import List, Tuple, Dict
import logging

def analyze_colors(image: Image.Image, n_colors: int = 5) -> List[Tuple[np.ndarray, float]]:
    """
    Analyze dominant colors in the image using K-means clustering.
    
    Args:
        image: PIL Image object
        n_colors: Number of dominant colors to extract
        
    Returns:
        List of tuples containing (RGB color array, percentage)
    """
    try:
        # Convert image to numpy array
        np_image = np.array(image)
        
        # Reshape the image to be a list of pixels
        pixels = np_image.reshape(-1, 3)
        
        # Use KMeans to find dominant colors
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get the colors and their percentages
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        percentages = np.bincount(labels) / len(labels)
        
        # Sort colors by percentage
        color_percentages = list(zip(colors, percentages))
        color_percentages.sort(key=lambda x: x[1], reverse=True)
        
        return color_percentages
    except Exception as e:
        logging.error(f"Error in color analysis: {str(e)}")
        return []
    
def detect_text(image: Image.Image) -> Dict[str, any]:
    try:
        img_array = np.array(image)
        reader = easyocr.Reader(['en'], gpu= False )
        results = reader.readtext(image)
        
        filtered_text = []
        confidences = []
        positions = []
        
        for bbox, text, conf in results:
            filtered_text.append(text)
            confidences.append(conf)
            positions.append({
                'left': int(bbox[0][0]),
                'top': int(bbox[0][1]),
                'width': int(bbox[2][0] - bbox[0][0]),
                'height': int(bbox[2][1] - bbox[0][1])
            })
            
        return {
            'text': filtered_text,
            'confidences': confidences,
            'positions': positions,
            'full_text': ' '.join(filtered_text)
        }
    except Exception as e:
        logging.error(f"Error in text detection: {str(e)}")
        return {'text': [], 'confidences': [], 'positions': [], 'full_text': ''}



def analyze_image_composition(image: Image.Image) -> Dict[str, float]:
    """
    Analyze the composition of the image including rule of thirds and visual balance
    using PIL and numpy instead of OpenCV.
    
    Args:
        image: PIL Image object
        
    Returns:
        Dictionary containing composition analysis results
    """
    try:
        # Convert image to grayscale using PIL
        gray_image = image.convert('L')
        
        # Convert to numpy array for calculations
        np_image = np.array(gray_image)
        height, width = np_image.shape
        
        # Calculate rule of thirds points
        third_h = height // 3
        third_w = width // 3
        
        # Create masks for different regions
        thirds_mask = np.zeros((height, width))
        thirds_mask[third_h:2*third_h, third_w:2*third_w] = 1
        
        # Calculate brightness in different regions
        # Using numpy operations directly on grayscale array
        left_brightness = np.mean(np_image[:, :width//2])
        right_brightness = np.mean(np_image[:, width//2:])
        top_brightness = np.mean(np_image[:height//2, :])
        bottom_brightness = np.mean(np_image[height//2:, :])
        
        # Normalize values between 0 and 1
        max_pixel_value = 255.0
        
        analysis_results = {
            'balance_horizontal': abs(left_brightness - right_brightness) / max_pixel_value,
            'balance_vertical': abs(top_brightness - bottom_brightness) / max_pixel_value,
            'thirds_intensity': np.mean(np_image * thirds_mask) / max_pixel_value,
            'overall_brightness': np.mean(np_image) / max_pixel_value
        }
        
        # Add additional composition metrics
        
        # Calculate edge density using Sobel-like operations
        dx = np.diff(np_image, axis=1, prepend=np_image[:, :1])
        dy = np.diff(np_image, axis=0, prepend=np_image[:1, :])
        edge_magnitude = np.sqrt(dx**2 + dy**2)
        analysis_results['edge_density'] = np.mean(edge_magnitude) / max_pixel_value
        
        # Calculate contrast
        contrast = np.std(np_image) / max_pixel_value
        analysis_results['contrast'] = contrast
        
        return analysis_results
        
    except Exception as e:
        logging.error(f"Error in composition analysis: {str(e)}")
        return {
            'balance_horizontal': 0,
            'balance_vertical': 0,
            'thirds_intensity': 0,
            'overall_brightness': 0,
            'edge_density': 0,
            'contrast': 0
        }

def get_composition_insights(analysis_results: Dict[str, float]) -> Dict[str, str]:
    """
    Generate human-readable insights from the composition analysis results.
    
    Args:
        analysis_results: Dictionary containing composition metrics
        
    Returns:
        Dictionary containing insights and suggestions
    """
    insights = {}
    
    # Analyze horizontal balance
    if analysis_results['balance_horizontal'] < 0.1:
        insights['balance'] = "The image has good horizontal balance"
    else:
        insights['balance'] = "Consider rebalancing elements horizontally"
    
    # Analyze brightness
    if analysis_results['overall_brightness'] < 0.3:
        insights['brightness'] = "The image might be too dark"
    elif analysis_results['overall_brightness'] > 0.7:
        insights['brightness'] = "The image might be too bright"
    else:
        insights['brightness'] = "Good overall brightness"
    
    # Analyze rule of thirds
    if analysis_results['thirds_intensity'] > 0.4:
        insights['composition'] = "Good use of rule of thirds"
    else:
        insights['composition'] = "Consider placing key elements at rule of thirds intersections"
    
    # Analyze contrast
    if analysis_results['contrast'] < 0.15:
        insights['contrast'] = "Consider increasing image contrast"
    elif analysis_results['contrast'] > 0.5:
        insights['contrast'] = "Good contrast level"
    
    return insights


def detect_faces(image: Image.Image) -> List[Tuple[int, int, int, int]]:
    """
    Detect faces in the image and return their locations.
    
    Args:
        image: PIL Image object
        
    Returns:
        List of tuples containing face locations (top, right, bottom, left)
    """
    try:
        # Convert PIL image to numpy array
        np_image = np.array(image)
        
        # Convert RGB to BGR for cv2
        if len(np_image.shape) == 3:  # Color image
            np_image = np_image[:, :, ::-1]
        
        # Detect faces using face_recognition library
        face_locations = face_recognition.face_locations(np_image)
        
        return face_locations
    except Exception as e:
        logging.error(f"Error in face detection: {str(e)}")
        return []
        

















