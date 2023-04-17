#import logging
#import logging.handlers
#import queue
import threading
import time
#import urllib.request
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
import googletrans
menu_nuoc=[]
ma_nuocs=googletrans.LANGUAGES
menu_nuoc.append('')
for ma_nuoc in ma_nuocs:
    menu_nuoc.append(ma_nuoc)
    

#if buton!='':    

def ds_nuoc(metric_raw):
    return ma_nuocs[metric_raw]
    
    

buton=st.selectbox('Chọn sàn giao dịch: ',options = ma_nuocs,format_func=ds_nuoc,key='nuoc')
if buton!='':
    st.write(buton)


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
    
    

    if not webrtc_ctx.state.playing:
        return

    text=[]
    text_output = st.empty()
    nut_radio=st.radio("Phiên dịch",["Tự động - phiên dịch", "Nhấn nút phiên dịch"])
    if nut_radio=="Tự động - phiên dịch":
        st.warning('phần tự động yêu cầu tiến ồn thấp')
        run = st.checkbox('Run')
        while run:
            if webrtc_ctx.state.playing:           
                
                sound_chunk = pydub.AudioSegment.empty()
                audio_frames = []
                with frames_deque_lock:
                    while len(frames_deque) > 0:
                        frame = frames_deque.popleft()
                        audio_frames.append(frame)

                if len(audio_frames) == 0:
                    time.sleep(0.1)
                    
                    continue           

                for audio_frame in audio_frames:
                    sound = pydub.AudioSegment(
                        data=audio_frame.to_ndarray().tobytes(),
                        sample_width=audio_frame.format.bytes,
                        frame_rate=audio_frame.sample_rate,
                        channels=len(audio_frame.layout.channels),
                    )
                    sound_chunk += sound

                
                    
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    text_output.markdown("Mời bạn nói: ")
                    
                    #st.write("Mời bạn nói:")
                    print("Mời bạn nói:")
                    if len(sound_chunk) > 0:    
                        audio = r.listen(source)
                        try:
                            
                            #text1=r.recognize_google(audio,language="vi-VI")
                            text1=r.recognize_google(audio)
                            print("Bạn -->: {}".format(text1))
                            
                            text_output.markdown(f"**Text:** {text1}")
                            st.write(f"**Text:** {text1}")   
                            
                            
                        except:
                            print("Xin lỗi! tôi không nhận được voice!")
                            text_output.markdown("Xin lỗi! tôi không nhận được voice!, hoặc quá ồn")
                            time.sleep(2)
    if nut_radio=="Nhấn nút phiên dịch":
        #st.warning('phần tự động yêu cầu tiến ồn thấp')
        
        if webrtc_ctx.state.playing: 
                run = st.checkbox('Run')
                while run:
                    r = sr.Recognizer()
                    with sr.Microphone() as source:
                            text_output.markdown("Mời bạn nói: ")                    
                            #st.write("Mời bạn nói:")
                            print("Mời bạn nói:")
                            audio = r.listen(source)
                            try:
                                
                                text1=r.recognize_google(audio,language="vi-VI")
                                
                                print("Bạn -->: {}".format(text1))
                                
                                text_output.markdown(f"**Text:** {text1}")
                                st.write(f"**Text:** {text1}")   
                                
                                
                            except:
                                print("Xin lỗi! tôi không nhận được voice!")
                                text_output.markdown("Xin lỗi! tôi không nhận được voice!, hoặc quá ồn")                                
                                time.sleep(2)                   
                       #st.write("Xin lỗi! tôi không nhận được voice!") 
                               
   
         
   
                
#app_sst_with_video()

