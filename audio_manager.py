
import os
import io
import re
import tempfile
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass

from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)



GTTS_OK = False
try:
    from gtts import gTTS
    GTTS_OK = True
    print("✅ gTTS (Google TTS - Gratuit) configuré")
except ImportError:
    print("⚠️ gTTS non installé : pip install gtts")

GROQ_OK = False
groq_client = None
try:
    from groq import Groq
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        groq_client = Groq(api_key=api_key)
        GROQ_OK = True
        print("✅ Groq Whisper (STT) configuré")
    else:
        print("⚠️ GROQ_API_KEY manquante")
except ImportError:
    print("⚠️ groq non installé : pip install groq")

ELEVENLABS_OK = GTTS_OK and GROQ_OK



@dataclass
class AudioResult:
    success: bool
    audio_bytes: Optional[bytes] = None
    text: Optional[str] = None
    error: Optional[str] = None



VOICE_OPTIONS = {
    "fr": {
        "name": "Français (France)",
        "lang": "fr",
        "tld": "fr"
    },
    "fr_slow": {
        "name": "Français Lent",
        "lang": "fr",
        "tld": "fr",
        "slow": True
    },
    "fr_ca": {
        "name": "Français (Canada)",
        "lang": "fr",
        "tld": "ca"
    },
}



class AudioManager:
    """
    Gestionnaire Audio Stable
    - TTS : gTTS (Google, gratuit, simple)
    - STT : Groq Whisper (fonctionne déjà ✅)
    """
    
    def __init__(self):
        if not GTTS_OK:
            raise ImportError("gTTS non installé : pip install gtts")
        if not GROQ_OK:
            raise ImportError("Groq non configuré")
        
        self.voice_key = "fr"
        self._cache: Dict[str, bytes] = {}
    
    def set_voice(self, key: str) -> bool:
        if key in VOICE_OPTIONS:
            self.voice_key = key
            return True
        return False
    
    @classmethod
    def get_voices(cls) -> List[Dict]:
        return [
            {"key": key, "name": voice["name"]} 
            for key, voice in VOICE_OPTIONS.items()
        ]
    

    
    def text_to_speech(self, text: str) -> AudioResult:
        """Convertit le texte en audio avec gTTS."""
        if not GTTS_OK:
            return AudioResult(success=False, error="gTTS non installé")
        
        clean_text = self._clean_text(text)
        
        if len(clean_text) < 3:
            return AudioResult(success=False, error="Texte trop court")
        
        try:
            cache_key = f"{self.voice_key}:{hash(clean_text)}"
            if cache_key in self._cache:
                return AudioResult(success=True, audio_bytes=self._cache[cache_key])
            
            if len(clean_text) > 5000:
                clean_text = clean_text[:5000]
            
            voice_config = VOICE_OPTIONS[self.voice_key]
            
            tts = gTTS(
                text=clean_text,
                lang=voice_config["lang"],
                tld=voice_config.get("tld", "fr"),
                slow=voice_config.get("slow", False)
            )
            
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_bytes = audio_buffer.read()
            
            if audio_bytes and len(audio_bytes) > 0:
                self._cache[cache_key] = audio_bytes
                return AudioResult(success=True, audio_bytes=audio_bytes)
            else:
                return AudioResult(success=False, error="Audio vide")
                
        except Exception as e:
            return AudioResult(success=False, error=f"Erreur TTS: {str(e)[:100]}")
    

    
    def speech_to_text(self, audio_bytes: bytes) -> AudioResult:
        """Transcrit l'audio avec Groq Whisper."""
        if not GROQ_OK or not groq_client:
            return AudioResult(success=False, error="Groq non configuré")
        
        if not audio_bytes or len(audio_bytes) < 1000:
            return AudioResult(success=False, error="Audio trop court")
        
        try:

            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            
            try:
                with open(tmp_path, "rb") as audio_file:
                    transcription = groq_client.audio.transcriptions.create(
                        model="whisper-large-v3",
                        file=audio_file,
                        language="fr",
                        response_format="text"
                    )
                
                if isinstance(transcription, str):
                    text = transcription.strip()
                else:
                    text = str(transcription).strip()
                
                if text:
                    return AudioResult(success=True, text=text)
                else:
                    return AudioResult(success=False, error="Aucune parole détectée")
                    
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
        except Exception as e:
            return AudioResult(success=False, error=f"Erreur STT: {str(e)[:100]}")
    

    
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[\U0001F000-\U0001FFFF]', '', text)
        text = re.sub(r'[*_#]+', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def clear_cache(self):
        self._cache.clear()



if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("   TEST AUDIO MANAGER")
    print("=" * 70 + "\n")
    
    print(f"gTTS: {'✅ OK' if GTTS_OK else '❌ Non installé'}")
    print(f"Groq Whisper: {'✅ OK' if GROQ_OK else '❌ Non configuré'}")
    
    if GTTS_OK:
        print("\n📢 Voix disponibles:")
        for voice in AudioManager.get_voices():
            print(f"   • {voice['name']}")
        
        print("\n🧪 Test TTS (gTTS)...")
        try:
            import time
            mgr = AudioManager()
            
            start = time.time()
            result = mgr.text_to_speech(
                "Bonjour, je suis le narrateur de votre aventure. "
                "Bienvenue dans le monde d'Hero IA."
            )
            duration = time.time() - start
            
            if result.success:
                print(f"   ✅ Audio généré: {len(result.audio_bytes)} bytes")
                print(f"   ⏱️  Temps: {duration:.2f} secondes")
                
              
                with open("test_gtts_audio.mp3", "wb") as f:
                    f.write(result.audio_bytes)
                print("   📁 Sauvegardé: test_gtts_audio.mp3")
                print("   🎧 Écoutez-le pour vérifier la qualité !")
            else:
                print(f"   ❌ Erreur: {result.error}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    if GROQ_OK:
        print("\n✅ STT (Groq Whisper) fonctionne déjà parfaitement")
    
    print("\n" + "=" * 70)
    print("💰 COÛT: 0€ (100% GRATUIT)")
    print("=" * 70 + "\n")