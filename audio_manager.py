# ============================================
# HERO IA - Audio Manager (TTS + STT)
# ElevenLabs - Version Corrigée
# ============================================

import os
import io
import re
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass

from dotenv import load_dotenv

# Charge le .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# ============================================
# VÉRIFICATION ELEVENLABS
# ============================================

ELEVENLABS_OK = False
elevenlabs_client = None

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    
    api_key = os.getenv("ELEVEN_LABS_KEY")
    
    if api_key:
        elevenlabs_client = ElevenLabs(api_key=api_key)
        ELEVENLABS_OK = True
        print("✅ ElevenLabs (TTS/STT) configuré")
    else:
        print("⚠️ ELEVEN_LABS_KEY manquante dans .env")
        
except ImportError:
    print("⚠️ ElevenLabs non installé : pip install elevenlabs")
except Exception as e:
    print(f"⚠️ Erreur ElevenLabs : {e}")


# ============================================
# DATA CLASSES
# ============================================

@dataclass
class AudioResult:
    success: bool
    audio_bytes: Optional[bytes] = None
    text: Optional[str] = None
    error: Optional[str] = None


# ============================================
# VOIX DISPONIBLES
# ============================================

VOICE_OPTIONS = {
    "adam": {
        "name": "Adam (Narrateur)",
        "id": "pNInz6obpgDQGcFmaJgB"
    },
    "arnold": {
        "name": "Arnold (Grave)",
        "id": "VR6AewLTigWG4xSOukaG"
    },
    "bella": {
        "name": "Bella (Féminin)",
        "id": "EXAVITQu4vr4xnSDxMaL"
    },
    "josh": {
        "name": "Josh (Dynamique)",
        "id": "TxGEqnHWrfWFTfGW9XjX"
    },
    "rachel": {
        "name": "Rachel (Doux)",
        "id": "21m00Tcm4TlvDq8ikWAM"
    },
}


# ============================================
# AUDIO MANAGER CLASS
# ============================================

class AudioManager:
    """Gestionnaire Audio - TTS et STT via ElevenLabs."""
    
    def __init__(self):
        if not ELEVENLABS_OK:
            raise ImportError("ElevenLabs non configuré")
        
        self.client = elevenlabs_client
        self.voice_id = VOICE_OPTIONS["adam"]["id"]
        self.voice_key = "adam"
        self._cache: Dict[str, bytes] = {}
    
    def set_voice(self, key: str) -> bool:
        if key in VOICE_OPTIONS:
            self.voice_id = VOICE_OPTIONS[key]["id"]
            self.voice_key = key
            return True
        return False
    
    @classmethod
    def get_voices(cls) -> List[Dict]:
        return [
            {"key": key, "name": voice["name"]} 
            for key, voice in VOICE_OPTIONS.items()
        ]
    
    # ==========================================
    # TTS - TEXT TO SPEECH
    # ==========================================
    
    def text_to_speech(self, text: str) -> AudioResult:
        """Convertit le texte en audio."""
        if not ELEVENLABS_OK or not self.client:
            return AudioResult(success=False, error="ElevenLabs non configuré")
        
        clean_text = self._clean_text(text)
        
        if len(clean_text) < 3:
            return AudioResult(success=False, error="Texte trop court")
        
        try:
            # Cache
            cache_key = f"{self.voice_id}:{hash(clean_text)}"
            if cache_key in self._cache:
                return AudioResult(success=True, audio_bytes=self._cache[cache_key])
            
            # Limite longueur
            if len(clean_text) > 5000:
                clean_text = clean_text[:5000]
            
            # Génère l'audio avec le modèle multilingual (plus stable)
            audio_generator = self.client.text_to_speech.convert(
                text=clean_text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            
            # Convertit en bytes
            audio_bytes = b"".join(audio_generator)
            
            if audio_bytes and len(audio_bytes) > 0:
                self._cache[cache_key] = audio_bytes
                return AudioResult(success=True, audio_bytes=audio_bytes)
            else:
                return AudioResult(success=False, error="Audio vide généré")
                
        except Exception as e:
            error_str = str(e)
            
            # Analyse l'erreur
            if "quota" in error_str.lower() or "limit" in error_str.lower():
                return AudioResult(success=False, error="Quota ElevenLabs épuisé")
            elif "unauthorized" in error_str.lower() or "401" in error_str:
                return AudioResult(success=False, error="Clé ElevenLabs invalide")
            elif "voice" in error_str.lower() and "not found" in error_str.lower():
                return AudioResult(success=False, error="Voix non trouvée")
            elif "model" in error_str.lower():
                return AudioResult(success=False, error="Modèle non disponible")
            else:
                # Affiche l'erreur complète pour debug
                print(f"DEBUG TTS Error: {error_str}")
                return AudioResult(success=False, error="Erreur TTS - Vérifiez vos crédits ElevenLabs")
    
    # ==========================================
    # STT - SPEECH TO TEXT
    # ==========================================
    
    def speech_to_text(self, audio_bytes: bytes) -> AudioResult:
        """Transcrit l'audio en texte."""
        if not ELEVENLABS_OK or not self.client:
            return AudioResult(success=False, error="ElevenLabs non configuré")
        
        if not audio_bytes:
            return AudioResult(success=False, error="Audio vide")
        
        if len(audio_bytes) < 1000:
            return AudioResult(success=False, error="Audio trop court")
        
        try:
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
            
            if text and len(text) > 0:
                return AudioResult(success=True, text=text)
            else:
                return AudioResult(success=False, error="Aucune parole détectée")
                
        except Exception as e:
            error_str = str(e)
            print(f"DEBUG STT Error: {error_str}")
            
            if "Could not process" in error_str:
                return AudioResult(success=False, error="Format audio non reconnu")
            else:
                return AudioResult(success=False, error="Erreur transcription")
    
    # ==========================================
    # UTILITAIRES
    # ==========================================
    
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[\U0001F000-\U0001FFFF]', '', text)
        text = re.sub(r'[*_#]+', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   TEST AUDIO MANAGER")
    print("=" * 60 + "\n")
    
    print(f"ElevenLabs: {'✅ OK' if ELEVENLABS_OK else '❌ Non configuré'}")
    
    if ELEVENLABS_OK:
        print("\n📢 Voix disponibles:")
        for voice in AudioManager.get_voices():
            print(f"   • {voice['name']} ({voice['key']})")
        
        print("\n🧪 Test TTS...")
        try:
            mgr = AudioManager()
            result = mgr.text_to_speech("Bonjour, ceci est un test.")
            
            if result.success:
                print(f"   ✅ Audio généré: {len(result.audio_bytes)} bytes")
                
                # Sauvegarde pour vérifier
                with open("test_audio.mp3", "wb") as f:
                    f.write(result.audio_bytes)
                print("   📁 Sauvegardé: test_audio.mp3")
            else:
                print(f"   ❌ Erreur: {result.error}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 60 + "\n")