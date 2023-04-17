#import speech_recognition as sr
from gtts import gTTS

#import playsound
from playsound import playsound
import os
import time


    
ma='vi'    
def speak(text,ma):   
        tts = gTTS(text=text, lang=ma,slow=True)
        filename = 'audio.mp3'        
        tts.save(filename)        
        playsound(filename)
        os.remove(filename)
       
    
 
speak(text="tao đang ở nhà",ma=ma)  
   

#text_to_speech("tao đang ở nhà")