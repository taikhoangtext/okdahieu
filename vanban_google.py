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

from googletrans import Translator
from gtts import gTTS
from playsound import playsound
import os

menu_nuocs=[]
ma_nuocs=googletrans.LANGUAGES
ma_nuocs['aaaa']="Việt Nam"

for ma_nuoc in ma_nuocs:
    menu_nuocs.append(ma_nuoc)
    
menu_nuocs.sort(reverse=False)

#for menu_nuoc in menu_nuocs:       
#    print(menu_nuoc,"sdsd",ma_nuocs[menu_nuoc])
    

#if buton!='':    

def ds_nuoc(metric_raw):
    return ma_nuocs[metric_raw]
    
    

def speak(text,ma):   
        tts = gTTS(text=text, lang=ma,slow=True)
        filename = 'audio.mp3'        
        tts.save(filename)        
        playsound(filename)
        os.remove(filename)


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
    
    nut_radio=st.radio("Phiên dịch",["Không phiên dịch","Tự động - phiên dịch"])
    
    if nut_radio=="Tự động - phiên dịch":
        ma_quocgia="vi"
        buton=st.selectbox('Chọn ngôn ngữ của bạn: ',options = menu_nuocs,format_func=ds_nuoc,key='nuoc')
        if buton:
            if buton=="aaaa":        
                ma_quocgia="vi"
            else:
                ma_quocgia=buton
        
        ma_quocgia_dich="vi"
        buton1=st.selectbox('Chọn ngôn cần dịch: ',options = menu_nuocs,format_func=ds_nuoc,key='nuoc_dich')
        if buton1:
            if buton1=="aaaa":        
                ma_quocgia_dich="vi"
            else:
                ma_quocgia_dich=buton1       
                
        text=[]
        text_output = st.empty()
        
        #if nut_radio=="Tự động - phiên dịch":
        # st.warning('phần tự động yêu cầu tiến ồn thấp')
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
                translator = Translator()
                
                with sr.Microphone() as source:
                    #with st.spinner('Wait for it...'):
                    text_output.warning("Mời bạn nói:............ ")
                    text1=''
                    #st.write("Mời bạn nói:")
                    print("Mời bạn nói:...........")
                    if len(sound_chunk) > 0: 
                          
                        audio = r.listen(source)
                        try:
                            text_output.success("Đã nhận") 
                            
                            text1=r.recognize_google(audio,language=ma_quocgia)
                            
                            
                            print("Bạn -->: {}".format(text1))
                           # 
                            text_output.markdown(f"**Text:** {text1}")
                            st.write(f"**Text:** {text1}") 
                            #
                              
                            
                            
                        except:
                            print("Xin lỗi! tôi không nhận được voice!")
                            text_output.markdown("**** Xin lỗi! tôi không nhận được voice!, hoặc quá ồn *****")
                            time.sleep(0.5)
                if text1!='':    
                    try:
                        result = translator.translate(text1, src=ma_quocgia, dest=ma_quocgia_dich)
                        print("dịch -->:{}".format(result.text))
                        st.write(f"**dịch :** {result.text}") 
                        #speak(result.text)
                        speak(text1=result.text1,ma=ma_quocgia_dich)
                    except:
                        print("Xin lỗi! phair co 2 nguoi")
                        text_output.warning("Xin lỗi! phai co nhom 2 nguoi")
app_sst_with_video()

