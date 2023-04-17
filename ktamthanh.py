import logging
import logging.handlers
import queue
import threading
import time
import urllib.request
from collections import deque
from pathlib import Path
from typing import List

import av
import numpy as np
import pydub
import streamlit as st

from streamlit_webrtc import WebRtcMode, webrtc_streamer
import speech_recognition as sr
import pyaudio
r = sr.Recognizer()
amthanh='temp.wav'
def app_sst_with_video(
   
):
    frames_deque_lock = threading.Lock()
    frames_deque: deque = deque([])

    async def queued_audio_frames_callback(
        frames: List[av.AudioFrame],
    ) -> av.AudioFrame:
        with frames_deque_lock:
            frames_deque.extend(frames)

        # Return empty frames to be silent.
        new_frames = []
        for frame in frames:
            input_array = frame.to_ndarray()
            new_frame = av.AudioFrame.from_ndarray(
                np.zeros(input_array.shape, dtype=input_array.dtype),
                layout=frame.layout.name,
            )
            new_frame.sample_rate = frame.sample_rate
            new_frames.append(new_frame)

        return new_frames

    webrtc_ctx = webrtc_streamer(
        key="speech-to-text-w-video",
        mode=WebRtcMode.SENDRECV,
        queued_audio_frames_callback=queued_audio_frames_callback,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": True},
    )
    
   
    run = st.checkbox('Run') 
    while run:
        if webrtc_ctx.state.playing:
                    with sr.Microphone() as source:
                        print("Mời bạn nói: ")
                        audio = r.listen(source)
                        try:
                            text = r.recognize_google(audio,language="vi-VI")
                            print("Bạn -->: {}".format(text))
                        except:
                            print("Xin lỗi! tôi không nhận được voice!")
                               
   
         
   
                
app_sst_with_video()

