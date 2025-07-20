import speech_recognition as sr

def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio)
        print(f"✅ You said: {query}")
        return query
    except sr.UnknownValueError:
        return "Sorry, I didn't catch that."
