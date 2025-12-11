# ============================================
# HERO IA - Audio Manager (TTS + STT)
# ============================================

import os
import io
import re
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass

from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

ELEVENLABS_OK = False
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    
    api_key = os.getenv("ELEVEN_LABS_KEY")
    if api_key:
        ELEVENLABS_OK = True
        print("✅ ElevenLabs (TTS/STT) configuré")
    else:
        print("⚠️ ELEVEN_LABS_KEY manquante")
except ImportError:
    print("⚠️ pip install elevenlabs")


@dataclass
class AudioResult:
    success: bool
    audio_bytes: Optional[bytes] = None
    text: Optional[str] = None
    error: Optional[str] = None


class AudioManager:
    
    VOICES = {
        "adam": {"name": "Adam (Narrateur)", "id": "pNInz6obpgDQGcFmaJgB"},
        "arnold": {"name": "Arnold (Grave)", "id": "VR6AewLTigWG4xSOukaG"},
        "bella": {"name": "Bella (Féminin)", "id": "EXAVITQu4vr4xnSDxMaL"},
        "josh": {"name": "Josh (Dynamique)", "id": "TxGEqnHWrfWFTfGW9XjX"},
        "rachel": {"name": "Rachel (Doux)", "id": "21m00Tcm4TlvDq8ikWAM"},
    }
    
    def __init__(self):
        if not ELEVENLABS_OK:
            raise ImportError("ElevenLabs non configuré")
        
        api_key = os.getenv("ELEVEN_LABS_KEY")
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = self.VOICES["adam"]["id"]
        self.voice_key = "adam"
        self._cache: Dict[str, bytes] = {}
    
    def set_voice(self, key: str):
        if key in self.VOICES:
            self.voice_id = self.VOICES[key]["id"]
            self.voice_key = key
    
    @classmethod
    def get_voices(cls) -> List[Dict]:
        return [{"key": k, "name": v["name"]} for k, v in cls.VOICES.items()]
    
    def text_to_speech(self, text: str) -> AudioResult:
        try:
            clean = self._clean_text(text)
            if len(clean) < 3:
                return AudioResult(success=False, error="Texte trop court")
            
            cache_key = f"{self.voice_id}:{hash(clean)}"
            if cache_key in self._cache:
                return AudioResult(success=True, audio_bytes=self._cache[cache_key])
            
            audio_generator = self.client.text_to_speech.convert(
                text=clean[:5000],
                voice_id=self.voice_id,
                model_id="eleven_flash_v2_5",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True
                )
            )
            
            audio_bytes = b"".join(audio_generator)
            
            if audio_bytes:
                self._cache[cache_key] = audio_bytes
                return AudioResult(success=True, audio_bytes=audio_bytes)
            
            return AudioResult(success=False, error="Audio vide")
            
        except Exception as e:
            return AudioResult(success=False, error=str(e)[:100])
    
    def speech_to_text(self, audio_bytes: bytes) -> AudioResult:
        try:
            if not audio_bytes or len(audio_bytes) < 1000:
                return AudioResult(success=False, error="Audio trop court")
            
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "recording.webm"
            
            result = self.client.speech_to_text.convert(
                file=audio_file,
                model_id="scribe_v1",
                language_code="fra"
            )
            
            if hasattr(result, 'text'):
                text = result.text.strip()
            else:
                text = str(result).strip()
            
            if text:
                return AudioResult(success=True, text=text)
            
            return AudioResult(success=False, error="Aucune parole détectée")
            
        except Exception as e:
            return AudioResult(success=False, error=str(e)[:100])
    
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[\U0001F000-\U0001FFFF]', '', text)
        text = re.sub(r'[*_#]+', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()