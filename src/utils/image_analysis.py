# src/utils/image_analysis.py

import numpy as np
from PIL import Image
# import cv2
# import face_recognition
# import pytesseract
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


























