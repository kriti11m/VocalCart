from gtts import gTTS
import os
import platform

def speak(text):
    print(f"🗣️ Speaking: {text}")
    tts = gTTS(text)
    tts.save("response.mp3")

    if platform.system() == "Windows":
        os.system("start response.mp3")
    elif platform.system() == "Darwin":  # macOS
        os.system("afplay response.mp3")
    else:  # Linux
        os.system("mpg321 response.mp3")
