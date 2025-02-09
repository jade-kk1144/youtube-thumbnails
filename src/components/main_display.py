# src/components/main_display.py
import streamlit as st
from utils.youtube import extract_video_id, get_thumbnail
from utils.image_analysis import (
    analyze_colors
    # detect_faces,
    ,detect_text
    # analyze_image_composition
)
# 
def show_main_display(sidebar_state):
    st.title("Thumbnail Analysis Results")
    
    if not sidebar_state['url']:
        st.info("Enter a YouTube URL in the sidebar to begin analysis")
        return
        
    # Extract video ID and get thumbnail
    video_id = extract_video_id(sidebar_state['url'])
    if not video_id:
        st.error("Invalid YouTube URL")
        return
        
    # Get and display thumbnail
    try:
        thumbnail = get_thumbnail(video_id)
        st.image(thumbnail, caption="Video Thumbnail", use_container_width=True)
        ``
        # Create tabs for different analyses
        if any(sidebar_state['options'].values()):
            tabs = []
            tab_names = []
            
            if sidebar_state['options']['color_analysis']:
                tab_names.append("Colors")
            # if sidebar_state['options']['face_detection']:
                # tab_names.append("Faces")
            # if sidebar_state['options']['text_detection']:
                # tab_names.append("Text")
            # if sidebar_state['options']['composition']:
                # tab_names.append("Composition")
                
            tabs = st.tabs(tab_names)
            
            # Fill each tab with its analysis
            current_tab = 0
            
            if sidebar_state['options']['color_analysis']:
                with tabs[current_tab]:
                    show_color_analysis(thumbnail, sidebar_state['settings'])
                current_tab += 1
                
            # if sidebar_state['options']['face_detection']:
                # with tabs[current_tab]:
                    # show_face_analysis(thumbnail, sidebar_state['settings'])
                # current_tab += 1
                # 
            if sidebar_state['options']['text_detection']:
                with tabs[current_tab]:
                    show_text_analysis(thumbnail, sidebar_state['settings'])
                current_tab += 1
                
            # if sidebar_state['options']['composition']:
                # with tabs[current_tab]:
                    # show_composition_analysis(thumbnail)
                # 
    except Exception as e:
        st.error(f"Error processing thumbnail: {str(e)}")

def show_color_analysis(image, settings):
    st.subheader("Color Analysis")
    colors = analyze_colors(image, settings['color_count'])
    # Display each color with its percentage
    for color, percentage in colors:
        # Create columns with specific widths
        col1, col2 = st.columns([1, 4])
        
        with col1:
            # Convert RGB tuple to CSS color string
            rgb_str = f"rgb({int(color[0])}, {int(color[1])}, {int(color[2])})"
            #  background-color: rgb{rgb_str};
            # Make sure the color block is visible with explicit dimensions
            st.markdown(
                f"""
                <div style="
                    background-color: rgb{int(color[0]),int(color[1]),int(color[2])};
                    width: 100px;
                    height: 50px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    display: inline-block;
                "></div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            # Vertically center the text with the color block
            st.markdown(
                f"""
                <div style="
                    line-height: 50px;
                    font-size: 16px;
                ">
                    {percentage:.1%} (RGB: {color[0]}, {color[1]}, {color[2]})
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Add some spacing between rows
        st.write("")

# 
# def show_face_analysis(image, settings):
    # st.subheader("Face Detection")
    # face_locations = detect_faces(image)
    # 
    # if face_locations:
        # st.write(f"Number of faces detected: {len(face_locations)}")
        # 
        # Display image with face boxes
        # import numpy as np
        # import cv2
        # 
        # np_image = np.array(image)
        # for top, right, bottom, left in face_locations:
            # cv2.rectangle(np_image, (left, top), (right, bottom), (0, 255, 0), 2)
        # st.image(np_image, caption="Faces Detected", use_column_width=True)
    # else:
        # st.write("No faces detected")

def show_text_analysis(image, settings):
    st.subheader("Text Analysis")
    text_data = detect_text(image)
    
    if text_data['text']:
        st.write("Detected Text:")
        for text, conf in zip(text_data['text'], text_data['confidences']):
            if conf >= settings['min_text_confidence']:
                st.write(f"- {text} (Confidence: {conf:.1f}%)")
    else:
        st.write("No text detected")

# def show_composition_analysis(image):
    # st.subheader("Composition Analysis")
    # composition = analyze_image_composition(image)
    # 
    # Display composition metrics
    # col1, col2 = st.columns(2)
    # with col1:
        # st.metric("Horizontal Balance", f"{(1 - composition['balance_horizontal']) * 100:.1f}%")
        # st.metric("Rule of Thirds Usage", f"{composition['thirds_intensity'] * 100:.1f}%")
    # with col2:
        # st.metric("Vertical Balance", f"{(1 - composition['balance_vertical']) * 100:.1f}%")
        # st.metric("Overall Brightness", f"{composition['overall_brightness'] * 100:.1f}%")