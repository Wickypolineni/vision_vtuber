import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import cv2
import io
from PIL import Image
from io import BytesIO
from pathlib import Path
import traceback
from lib.logger import Logger
from lib.video import ImageCV2

# Initialize session state
def init_session_state():
    if 'captured_image' not in st.session_state:
        st.session_state['captured_image'] = None
    if "logger" not in st.session_state:
        st.session_state["logger"] = None
    if "webrtc_ctx" not in st.session_state:
        st.session_state["webrtc_ctx"] = None

# Exception handling decorator
def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exception:
            st.session_state.logger.error(f"An error occurred in {func.__name__}: {exception}")
            st.error(f"An error occurred: {exception}")
            st.session_state.logger.error(traceback.format_exc())
            st.stop()
    return wrapper

@exception_handler
def validate_image(image_path):
    if not image_path.exists():
        st.session_state.logger.error(f"Could not find image: {image_path}")
        raise FileNotFoundError(f"Could not find image: {image_path}")
            
@exception_handler
def log_webrtc_context_states(webrtc_ctx):
    if webrtc_ctx is not None:
        # Log the state of the WebRTC context
        st.session_state.logger.info(f"WebRTC context: {webrtc_ctx}")
        st.session_state.logger.info(f"Is WebRTC playing: {webrtc_ctx.state.playing}")
        st.session_state.logger.info(f"Is audio receiver ready: {webrtc_ctx.audio_receiver}")
        st.session_state.logger.info(f"Is video receiver ready: {webrtc_ctx.video_receiver}")
    else:
        st.error("WebRTC context is None.")


@exception_handler
def capture_image():
    st.session_state.logger.info("Attempting to capture image from webcam with ImageCV2...")
    
    # Capture the image from the webcam
    web_image = None
    web_cam = ImageCV2()
 
    web_image_file = "web_image.png"
    web_image = web_cam.capture_image_from_webcam(web_image_file)
    if web_image is None:
        raise ValueError("Could not capture image from webcam")
    
    # convert web_image from RGB to RGBA
    web_image = web_image.convert("RGBA")
    
    # Validate that an image is present
    image_path = Path(web_image_file)
    validate_image(image_path)
    
    # Open the image
    st.session_state.logger.info(f"Trying to open image: {web_image_file}")
    web_image = Image.open(web_image_file)
    return web_image

def display_support():
    st.markdown("<div style='text-align: center;'>Ask me Anything</div>", unsafe_allow_html=True)
    


# Streamlit App
def streamlit_app():    
    
    # Google Logo and Title
    st.write('<div style="display: flex; flex-direction: row; align-items: center; justify-content: center;"><h1 style="margin-left: 10px;">Vision_tuber</h1></div>', unsafe_allow_html=True)
    
    # Display support
    display_support()

        
    # WebRTC streamer only if image is not captured
    webrtc_ctx = webrtc_streamer(
                key="webcam", 
                mode=WebRtcMode.SENDRECV, 
                rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
                video_frame_callback=lambda frame: None
            )
   
    col1 = st.columns(1)

    with col1:
        if st.button("Capture Image"):
            
            # Validate API Key
            if st.session_state.api_key is None or st.session_state.api_key == '':
                st.toast("Please enter API Key in the sidebar.", icon="❌")
                
            else:
                st.session_state['captured_image'] = capture_image()
                if st.session_state['captured_image'] is not None:
                    st.toast("Image captured successfully!")
                else:
                    st.warning("Failed to capture image. Please try again.")

    
    # if image is captured then display it
    if st.session_state['captured_image'] is not None:
        st.image(st.session_state['captured_image'], caption="Captured Image", use_column_width=True)
    
                    
if __name__ == "__main__":
    try:
        init_session_state()
        streamlit_app()
    except Exception as exception:
        import traceback