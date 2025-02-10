# src/components/main_display.py
import streamlit as st
import pandas as pd
from utils.youtube import (
    extract_video_id, get_thumbnail, get_video_details, 
    format_view_counts, calculate_video_metrics
)
from utils.image_analysis import (
    analyze_colors
    ,detect_faces
    ,detect_text
    ,analyze_image_composition
    ,get_composition_insights
)
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

    try:
        # Create two columns
        col1, col2 = st.columns([0.3, 0.7])

        with col1:
            st.subheader("Video Information")
            
            # Get video details
            
            thumbnail = get_thumbnail(video_id)
            
            # Display thumbnail with half width
            st.image(thumbnail, caption="Video Thumbnail", use_container_width=True)
            
            try:
                video_details = get_video_details(video_id, api_key=st.secrets["YOUTUBE_API_KEY"])
                video_data = calculate_video_metrics(video_details)
                st.markdown(f"**Channel:** {video_details['channel_name']}   **Subs:** {format_view_counts(video_details['subscriber_count'])}")
                st.markdown(f"**Title:** {video_details['title']}")
                st.markdown(f"**Views:** {format_view_counts(video_details['view_count'])}")
                st.markdown(
                         f"""
                         **Likes:** {format_view_counts(video_details['like_count'])}  **Comments:** {format_view_counts(video_details['comment_count'])}
                         """
                         )                       
                st.markdown(f"**Published:** {(video_details['published_date'])}")  
                st.write(video_details)                            
            except:
                st.error('api fail')
            # 
            # try:
            #   
            # Display video information
           
           
           
           

        with col2:
            st.subheader("Analysis Results")
        
            # Get and display thumbnail
            try:   
                # Create tabs for different analyses
                if any(sidebar_state['options'].values()):
                    tabs = []
                    tab_names = ["Metrics"]
                    if sidebar_state['options']['color_analysis']:
                        tab_names.append("Colors")
                    if sidebar_state['options']['face_detection']:
                        tab_names.append("Faces")
                    if sidebar_state['options']['text_detection']:
                        tab_names.append("Text")
                    if sidebar_state['options']['composition']:
                        tab_names.append("Composition")
                        
                    tabs = st.tabs(tab_names)
                    
                    # Fill each tab with its analysis
                    current_tab = 0
                    with tabs[0]:
                        display_metrics_tab(video_data)
                        current_tab += 1
                    if sidebar_state['options']['color_analysis']:
                        with tabs[current_tab]:
                            show_color_analysis(thumbnail, sidebar_state['settings'])
                        current_tab += 1
                        
                    if sidebar_state['options']['face_detection']:
                        with tabs[current_tab]:
                            show_face_analysis(thumbnail, sidebar_state['settings'])
                        current_tab += 1
                        
                    if sidebar_state['options']['text_detection']:
                        with tabs[current_tab]:
                            show_text_analysis(thumbnail, sidebar_state['settings'])
                        current_tab += 1
                        
                    if sidebar_state['options']['composition']:
                        with tabs[current_tab]:
                            show_composition_analysis(thumbnail)
                        
            except Exception as e:
                st.error(f"Error processing thumbnail: {str(e)}")
    except Exception as e:
        st.error("Error")


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
                    width: 30px;
                    height: 30px;
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


def show_face_analysis(image, settings):
    st.subheader("Face Detection")
    face_locations = detect_faces(image)
    
    if face_locations:
        st.write(f"Number of faces detected: {len(face_locations)}")
        
        # Display image with face boxes
    
        # 
        np_image = np.array(image)
        # for top, right, bottom, left in face_locations:
            # cv2.rectangle(np_image, (left, top), (right, bottom), (0, 255, 0), 2)
        st.image(np_image, caption="Faces Detected", use_column_width=True)
    else:
        st.write("No faces detected")

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


def show_composition_analysis(image):
    st.subheader("Composition Analysis")
    composition = analyze_image_composition(image)
    insights = get_composition_insights(composition)
    
    # Display metrics and insights in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Horizontal Balance", f"{(1 - composition['balance_horizontal']) * 100:.1f}%")
        st.markdown(f"*{insights['balance']}*")
        
        st.metric("Rule of Thirds Usage", f"{composition['thirds_intensity'] * 100:.1f}%")
        st.markdown(f"*{insights['composition']}*")
    
    with col2:
        st.metric("Vertical Balance", f"{(1 - composition['balance_vertical']) * 100:.1f}%")
        
        st.metric("Overall Brightness", f"{composition['overall_brightness'] * 100:.1f}%")
        st.markdown(f"*{insights['brightness']}*")
    
    # Display contrast insight if available
    if 'contrast' in insights:
        st.markdown(f"**Contrast Analysis:** *{insights['contrast']}*")
    
    # Display face detection results if available
    face_locations = detect_faces(image)
    if face_locations:
        st.markdown(f"**Faces Detected:** {len(face_locations)}")
        if len(face_locations) > 0:
            st.markdown("*Consider positioning faces along rule-of-thirds points for better engagement*")
    
def display_metrics_tab(video_data, comparison_metrics = None):
   metrics = calculate_video_metrics(video_data)
   
   # Default benchmarks
   default_benchmarks = {
       'engagement_score': 50,
       'like_ratio': 2.5,
       'comment_ratio': 0.3,
       'sub_conversion':2,
       'view_velocity':1000,
       'note': '* Using fixed average benchmarks from 2024 : engagement 50, like ratio: 2.5%; comment ratio: 0.3%, conversion: 2%'
   }
   
   benchmark = comparison_metrics if comparison_metrics else default_benchmarks
   
   col1, col2, col3 = st.columns(3)
   
   with col1:
       st.metric(
           "Overall Engagement", 
           f"{metrics['engagement_score']:.1f}/100",
           delta=round(metrics['engagement_score'] - benchmark['engagement_score'], 1)
       )
   
   with col2:
       st.metric(
           "Like Rate",
           f"{metrics['like_ratio']:.2f}%",
           delta=round(metrics['like_ratio'] - benchmark['like_ratio'], 2)
       )
   
   with col3:
       st.metric(
           "Comment Rate", 
           f"{metrics['comment_ratio']:.2f}%",
           delta=round(metrics['comment_ratio'] - benchmark['comment_ratio'], 2)
       )

   with st.expander("Detailed Metrics"):
        metrics_vs_benchmark = {
            'Sub Conversion (%)': [metrics['sub_conversion'], benchmark.get('sub_conversion', '-')],
            'Views/Day': [metrics['view_velocity'], benchmark.get('view_velocity', '-')]
        }

        df_metrics = pd.DataFrame(metrics_vs_benchmark, index=['Current', 'Benchmark'])

        # Format numbers
        for col in df_metrics.columns:
            if 'Ratio' in col or 'Conversion' in col:
                df_metrics[col] = df_metrics[col].apply(lambda x: f"{x:.1f}" if isinstance(x, (int, float)) else x)
            else:
                df_metrics[col] = df_metrics[col].apply(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x)

        st.table(df_metrics)
        if 'note' in benchmark:
            st.write(benchmark['note'])