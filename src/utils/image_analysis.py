# src/utils/image_analysis.py

import numpy as np
from PIL import Image
import cv2
import face_recognition
import pytesseract
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

def detect_text(image: Image.Image) -> Dict[str, any]:
    """
    Detect text in the image using pytesseract OCR.
    
    Args:
        image: PIL Image object
        
    Returns:
        Dictionary containing detected text and confidence scores
    """
    try:
        # Get detailed OCR data
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # Filter out low confidence detections and empty text
        filtered_text = []
        confidences = []
        positions = []
        
        for i, text in enumerate(ocr_data['text']):
            if int(ocr_data['conf'][i]) > 0 and text.strip():  # Filter empty text and low confidence
                filtered_text.append(text)
                confidences.append(float(ocr_data['conf'][i]))
                positions.append({
                    'left': ocr_data['left'][i],
                    'top': ocr_data['top'][i],
                    'width': ocr_data['width'][i],
                    'height': ocr_data['height'][i]
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

def create_heatmap(images: List[Image.Image], width: int = 1280, height: int = 720) -> np.ndarray:
    """
    Create a heatmap of face and text locations across multiple images.
    
    Args:
        images: List of PIL Image objects
        width: Standard width to resize images to
        height: Standard height to resize images to
        
    Returns:
        Numpy array representing the heatmap
    """
    try:
        heatmap = np.zeros((height, width))
        
        for image in images:
            # Resize image to standard size
            image = image.resize((width, height))
            
            # Add face locations to heatmap
            face_locations = detect_faces(image)
            for top, right, bottom, left in face_locations:
                heatmap[top:bottom, left:right] += 1
            
            # Add text locations to heatmap
            text_data = detect_text(image)
            for pos in text_data['positions']:
                left = pos['left']
                top = pos['top']
                right = left + pos['width']
                bottom = top + pos['height']
                
                # Ensure coordinates are within bounds
                left = max(0, min(left, width-1))
                right = max(0, min(right, width))
                top = max(0, min(top, height-1))
                bottom = max(0, min(bottom, height))
                
                heatmap[top:bottom, left:right] += 0.5
        
        # Normalize heatmap
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()
        
        return heatmap
    except Exception as e:
        logging.error(f"Error in heatmap creation: {str(e)}")
        return np.zeros((height, width))

def analyze_image_composition(image: Image.Image) -> Dict[str, any]:
    """
    Analyze the composition of the image including rule of thirds and visual balance.
    
    Args:
        image: PIL Image object
        
    Returns:
        Dictionary containing composition analysis results
    """
    try:
        # Convert to numpy array
        np_image = np.array(image)
        height, width = np_image.shape[:2]
        
        # Calculate rule of thirds points
        third_h = height // 3
        third_w = width // 3
        
        # Create masks for different regions
        thirds_mask = np.zeros((height, width))
        thirds_mask[third_h:2*third_h, third_w:2*third_w] = 1
        
        # Analyze brightness distribution
        if len(np_image.shape) == 3:  # Color image
            gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
        else:
            gray = np_image
            
        # Calculate brightness in different regions
        left_brightness = np.mean(gray[:, :width//2])
        right_brightness = np.mean(gray[:, width//2:])
        top_brightness = np.mean(gray[:height//2, :])
        bottom_brightness = np.mean(gray[height//2:, :])
        
        return {
            'balance_horizontal': abs(left_brightness - right_brightness) / 255,
            'balance_vertical': abs(top_brightness - bottom_brightness) / 255,
            'thirds_intensity': np.mean(gray * thirds_mask) / 255,
            'overall_brightness': np.mean(gray) / 255
        }
    except Exception as e:
        logging.error(f"Error in composition analysis: {str(e)}")
        return {
            'balance_horizontal': 0,
            'balance_vertical': 0,
            'thirds_intensity': 0,
            'overall_brightness': 0
        }