import logging
import io
import tempfile
import os
from typing import Optional, Dict, Any

# Voice input/output imports
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

logger = logging.getLogger(__name__)

class VoiceManager:
    """
    Centralized voice input/output management for VocalCart
    Handles speech recognition, text-to-speech, and audio processing
    """
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        
        # Initialize speech recognition
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            if PYAUDIO_AVAILABLE:
                try:
                    self.microphone = sr.Microphone()
                    # Adjust for ambient noise
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source)
                except Exception as e:
                    logger.warning(f"Microphone initialization failed: {e}")
        
        # Initialize TTS engine
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self._configure_tts_engine()
            except Exception as e:
                logger.warning(f"pyttsx3 initialization failed: {e}")
    
    def _configure_tts_engine(self):
        """Configure the pyttsx3 TTS engine with optimal settings"""
        if not self.tts_engine:
            return
        
        try:
            # Set speaking rate
            rate = self.tts_engine.getProperty('rate')
            self.tts_engine.setProperty('rate', max(150, rate - 50))  # Slower for clarity
            
            # Set volume
            volume = self.tts_engine.getProperty('volume')
            self.tts_engine.setProperty('volume', min(1.0, volume + 0.1))
            
            # Try to set a pleasant voice
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > 1:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
        except Exception as e:
            logger.debug(f"TTS configuration error: {e}")
    
    def listen_for_speech(self, timeout: int = 5, phrase_timeout: int = 2) -> Optional[str]:
        """
        Listen for speech input and convert to text
        Returns the recognized text or None if failed
        """
        if not self.recognizer or not self.microphone:
            logger.error("Speech recognition not available")
            return None
        
        try:
            logger.info("Listening for speech...")
            
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_timeout
                )
            
            # Recognize speech using Google's API
            try:
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Recognized: {text}")
                return text.strip()
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                return None
            except sr.RequestError as e:
                logger.error(f"Google Speech Recognition error: {e}")
                # Fallback to offline recognition if available
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    logger.info(f"Offline recognition: {text}")
                    return text.strip()
                except:
                    return None
        
        except sr.WaitTimeoutError:
            logger.warning("Speech recognition timeout")
            return None
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return None
    
    def speak_text(self, text: str, use_gtts: bool = False) -> bool:
        """
        Convert text to speech and play it
        Returns True if successful, False otherwise
        """
        if not text or len(text.strip()) == 0:
            return False
        
        try:
            if use_gtts and GTTS_AVAILABLE:
                return self._speak_with_gtts(text)
            elif self.tts_engine:
                return self._speak_with_pyttsx3(text)
            else:
                logger.error("No TTS engine available")
                return False
        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")
            return False
    
    def _speak_with_pyttsx3(self, text: str) -> bool:
        """Speak text using pyttsx3 (offline)"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"pyttsx3 speech error: {e}")
            return False
    
    def _speak_with_gtts(self, text: str) -> bool:
        """Speak text using gTTS (requires internet)"""
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file and play
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Try to play the audio file
                if os.name == 'posix':  # macOS/Linux
                    os.system(f"afplay {tmp_file.name}")
                elif os.name == 'nt':  # Windows
                    os.system(f"start {tmp_file.name}")
                
                # Cleanup
                os.unlink(tmp_file.name)
                return True
                
        except Exception as e:
            logger.error(f"gTTS speech error: {e}")
            return False
    
    def generate_audio_bytes(self, text: str, format: str = "mp3") -> Optional[bytes]:
        """
        Generate audio bytes for the given text
        Used for API responses
        """
        if not text or len(text.strip()) == 0:
            return None
        
        try:
            if format == "mp3" and GTTS_AVAILABLE:
                return self._generate_gtts_bytes(text)
            elif format == "wav" and self.tts_engine:
                return self._generate_pyttsx3_bytes(text)
            else:
                logger.error(f"Audio format {format} not supported")
                return None
        except Exception as e:
            logger.error(f"Audio generation error: {e}")
            return None
    
    def _generate_gtts_bytes(self, text: str) -> bytes:
        """Generate MP3 audio bytes using gTTS"""
        tts = gTTS(text=text, lang='en', slow=False)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            
            with open(tmp_file.name, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            os.unlink(tmp_file.name)
            return audio_data
    
    def _generate_pyttsx3_bytes(self, text: str) -> bytes:
        """Generate WAV audio bytes using pyttsx3"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            self.tts_engine.save_to_file(text, tmp_file.name)
            self.tts_engine.runAndWait()
            
            with open(tmp_file.name, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            os.unlink(tmp_file.name)
            return audio_data
    
    def get_voice_capabilities(self) -> Dict[str, Any]:
        """
        Get information about available voice capabilities
        """
        return {
            "speech_recognition": {
                "available": SPEECH_RECOGNITION_AVAILABLE,
                "microphone": self.microphone is not None,
                "engines": ["google", "sphinx"] if SPEECH_RECOGNITION_AVAILABLE else []
            },
            "text_to_speech": {
                "available": PYTTSX3_AVAILABLE or GTTS_AVAILABLE,
                "engines": {
                    "pyttsx3": PYTTSX3_AVAILABLE,
                    "gtts": GTTS_AVAILABLE
                },
                "voices": self._get_available_voices()
            },
            "audio_processing": {
                "pyaudio": PYAUDIO_AVAILABLE,
                "formats": ["mp3", "wav"]
            }
        }
    
    def _get_available_voices(self) -> list:
        """Get list of available voices"""
        voices = []
        if self.tts_engine:
            try:
                engine_voices = self.tts_engine.getProperty('voices')
                for voice in engine_voices:
                    voices.append({
                        "id": voice.id,
                        "name": voice.name,
                        "gender": "female" if "female" in voice.name.lower() else "male"
                    })
            except:
                pass
        return voices
    
    def test_voice_system(self) -> Dict[str, Any]:
        """
        Test the voice system and return status
        """
        results = {
            "speech_recognition": False,
            "text_to_speech": False,
            "microphone": False,
            "errors": []
        }
        
        # Test speech recognition
        if self.recognizer and self.microphone:
            try:
                # Quick ambient noise test
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                results["speech_recognition"] = True
                results["microphone"] = True
            except Exception as e:
                results["errors"].append(f"Speech recognition test failed: {e}")
        
        # Test TTS
        try:
            test_text = "Voice system test successful"
            if self.tts_engine:
                # Don't actually speak during test
                results["text_to_speech"] = True
            elif GTTS_AVAILABLE:
                results["text_to_speech"] = True
        except Exception as e:
            results["errors"].append(f"TTS test failed: {e}")
        
        return results
    
    def cleanup(self):
        """Cleanup voice resources"""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
    
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup()

# Global voice manager instance
voice_manager = VoiceManager()

# Convenience functions for backward compatibility
def get_voice_input(timeout: int = 5) -> Optional[str]:
    """Get voice input - convenience function"""
    return voice_manager.listen_for_speech(timeout=timeout)

def speak(text: str, use_gtts: bool = False) -> bool:
    """Speak text - convenience function"""
    return voice_manager.speak_text(text, use_gtts=use_gtts)
