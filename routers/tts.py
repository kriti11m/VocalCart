from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import logging
import io
import tempfile
import os

# Import TTS libraries
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

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "en"
    speed: Optional[float] = 1.0
    voice: Optional[str] = "default"  # "male", "female", "default"

class TTSEngine:
    """Text-to-Speech engine with multiple backend support"""
    
    def __init__(self):
        self.gtts_available = GTTS_AVAILABLE
        self.pyttsx3_available = PYTTSX3_AVAILABLE
        self.pyttsx3_engine = None
        
        if self.pyttsx3_available:
            try:
                self.pyttsx3_engine = pyttsx3.init()
            except:
                self.pyttsx3_available = False
                logger.warning("pyttsx3 initialization failed")
    
    def generate_audio_gtts(self, text: str, language: str = "en") -> bytes:
        """Generate audio using Google TTS"""
        if not self.gtts_available:
            raise Exception("gTTS not available")
        
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Read audio data
                with open(tmp_file.name, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                # Cleanup
                os.unlink(tmp_file.name)
                
                return audio_data
                
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            raise
    
    def generate_audio_pyttsx3(self, text: str, voice: str = "default", speed: float = 1.0) -> bytes:
        """Generate audio using pyttsx3 (offline)"""
        if not self.pyttsx3_available or not self.pyttsx3_engine:
            raise Exception("pyttsx3 not available")
        
        try:
            # Configure voice settings
            voices = self.pyttsx3_engine.getProperty('voices')
            
            if voice == "female" and len(voices) > 1:
                self.pyttsx3_engine.setProperty('voice', voices[1].id)
            elif voice == "male" and len(voices) > 0:
                self.pyttsx3_engine.setProperty('voice', voices[0].id)
            
            # Set speaking rate
            rate = self.pyttsx3_engine.getProperty('rate')
            self.pyttsx3_engine.setProperty('rate', int(rate * speed))
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                self.pyttsx3_engine.save_to_file(text, tmp_file.name)
                self.pyttsx3_engine.runAndWait()
                
                # Read audio data
                with open(tmp_file.name, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                # Cleanup
                os.unlink(tmp_file.name)
                
                return audio_data
                
        except Exception as e:
            logger.error(f"pyttsx3 error: {e}")
            raise
    
    def get_available_engines(self) -> list:
        """Get list of available TTS engines"""
        engines = []
        if self.gtts_available:
            engines.append("gtts")
        if self.pyttsx3_available:
            engines.append("pyttsx3")
        return engines

# Initialize TTS engine
tts_engine = TTSEngine()

@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech and return audio stream
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 1000:
            raise HTTPException(status_code=400, detail="Text too long (max 1000 characters)")
        
        logger.info(f"TTS request: {request.text[:50]}...")
        
        # Try gTTS first (better quality for online use)
        if tts_engine.gtts_available:
            try:
                audio_data = tts_engine.generate_audio_gtts(request.text, request.language)
                
                # Create streaming response
                audio_stream = io.BytesIO(audio_data)
                
                return StreamingResponse(
                    io.BytesIO(audio_data),
                    media_type="audio/mpeg",
                    headers={
                        "Content-Disposition": "attachment; filename=speech.mp3",
                        "Content-Length": str(len(audio_data))
                    }
                )
                
            except Exception as e:
                logger.warning(f"gTTS failed, trying pyttsx3: {e}")
        
        # Fallback to pyttsx3
        if tts_engine.pyttsx3_available:
            try:
                audio_data = tts_engine.generate_audio_pyttsx3(
                    request.text, 
                    request.voice, 
                    request.speed
                )
                
                return StreamingResponse(
                    io.BytesIO(audio_data),
                    media_type="audio/wav",
                    headers={
                        "Content-Disposition": "attachment; filename=speech.wav",
                        "Content-Length": str(len(audio_data))
                    }
                )
                
            except Exception as e:
                logger.error(f"pyttsx3 also failed: {e}")
        
        # If all engines fail, return error
        raise HTTPException(
            status_code=503, 
            detail="TTS service unavailable. No working TTS engines found."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts/quick")
async def quick_tts(text: str):
    """
    Quick TTS endpoint for simple text conversion
    """
    request = TTSRequest(text=text)
    return await text_to_speech(request)

@router.get("/tts/test")
async def test_tts():
    """
    Test TTS functionality with a sample text
    """
    test_text = "Welcome to VocalCart! Your voice-powered shopping assistant is working perfectly."
    
    try:
        request = TTSRequest(text=test_text)
        return await text_to_speech(request)
    except Exception as e:
        return {"error": str(e), "available_engines": tts_engine.get_available_engines()}

@router.get("/tts/engines")
async def get_tts_engines():
    """
    Get information about available TTS engines
    """
    return {
        "available_engines": tts_engine.get_available_engines(),
        "gtts_available": tts_engine.gtts_available,
        "pyttsx3_available": tts_engine.pyttsx3_available,
        "recommended": "gtts" if tts_engine.gtts_available else "pyttsx3"
    }

@router.post("/tts/product-announcement")
async def announce_product(product: dict):
    """
    Generate TTS for product announcements
    Formats product information into natural speech
    """
    try:
        # Format product information for natural speech
        title = product.get('title', 'Unknown product')
        price = product.get('price', 'Price not available')
        store = product.get('store', 'unknown store')
        rating = product.get('rating')
        
        # Create natural announcement
        announcement = f"{title}, priced at rupees {price}"
        
        if rating:
            announcement += f", with a rating of {rating} stars"
        
        announcement += f", available on {store}."
        
        # Add call to action
        announcement += " Say buy this to purchase, or next for more options."
        
        # Generate TTS
        request = TTSRequest(text=announcement)
        return await text_to_speech(request)
        
    except Exception as e:
        logger.error(f"Product announcement TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts/search-results")
async def announce_search_results(results: dict):
    """
    Generate TTS for search result summaries
    """
    try:
        products = results.get('products', [])
        query = results.get('query', 'your search')
        
        if not products:
            announcement = f"Sorry, I couldn't find any products for {query}. Please try different keywords."
        else:
            count = len(products)
            first_product = products[0]
            
            announcement = f"Found {count} products for {query}. "
            announcement += f"First result: {first_product.get('title', 'Unknown')} "
            announcement += f"for rupees {first_product.get('price', 'unknown price')}. "
            announcement += "Say next for more options, or buy this to purchase."
        
        # Generate TTS
        request = TTSRequest(text=announcement)
        return await text_to_speech(request)
        
    except Exception as e:
        logger.error(f"Search results TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
