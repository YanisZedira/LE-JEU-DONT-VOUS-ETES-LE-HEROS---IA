# ============================================
# DIAGNOSTIC COMPLET - Audio Manager
# ============================================

import os
import io
from pathlib import Path
from dotenv import load_dotenv

# Charge .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

print("\n" + "=" * 60)
print("   DIAGNOSTIC COMPLET AUDIO")
print("=" * 60)

# ============================================
# 1. VÉRIFICATION CLÉ API
# ============================================

print("\n1️⃣ VÉRIFICATION CLÉ API")
print("-" * 40)

api_key = os.getenv("ELEVEN_LABS_KEY")
if api_key:
    print(f"   ✅ Clé trouvée: {api_key[:15]}...")
else:
    print("   ❌ ELEVEN_LABS_KEY non trouvée dans .env")
    exit()

# ============================================
# 2. IMPORT ELEVENLABS
# ============================================

print("\n2️⃣ IMPORT ELEVENLABS")
print("-" * 40)

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    print("   ✅ elevenlabs importé")
except ImportError as e:
    print(f"   ❌ Import échoué: {e}")
    print("   → pip install elevenlabs")
    exit()

# ============================================
# 3. CONNEXION CLIENT
# ============================================

print("\n3️⃣ CONNEXION CLIENT")
print("-" * 40)

try:
    client = ElevenLabs(api_key=api_key)
    print("   ✅ Client créé")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    exit()

# ============================================
# 4. TEST TTS (Text-to-Speech)
# ============================================

print("\n4️⃣ TEST TTS (Text-to-Speech)")
print("-" * 40)

try:
    print("   ⏳ Génération audio...")
    
    audio_generator = client.text_to_speech.convert(
        text="Bonjour, ceci est un test du système audio.",
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    
    audio_bytes = b"".join(audio_generator)
    
    if audio_bytes and len(audio_bytes) > 0:
        print(f"   ✅ TTS OK - Audio généré: {len(audio_bytes)} bytes")
        
        # Sauvegarde pour test STT
        with open("test_tts_output.mp3", "wb") as f:
            f.write(audio_bytes)
        print("   📁 Sauvegardé: test_tts_output.mp3")
        
        tts_audio = audio_bytes
    else:
        print("   ❌ Audio vide")
        tts_audio = None
        
except Exception as e:
    print(f"   ❌ Erreur TTS: {e}")
    tts_audio = None

# ============================================
# 5. TEST STT (Speech-to-Text) avec fichier TTS
# ============================================

print("\n5️⃣ TEST STT (Speech-to-Text)")
print("-" * 40)

if tts_audio:
    try:
        print("   ⏳ Transcription de l'audio TTS...")
        
        audio_file = io.BytesIO(tts_audio)
        audio_file.name = "test.mp3"
        
        result = client.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1",
            language_code="fra"
        )
        
        # Affiche le résultat brut
        print(f"   📋 Résultat brut: {type(result)}")
        print(f"   📋 Contenu: {result}")
        
        if hasattr(result, 'text'):
            text = result.text
            print(f"   ✅ STT OK - Texte: \"{text}\"")
        else:
            print(f"   ⚠️ Pas d'attribut 'text', résultat: {result}")
            
    except Exception as e:
        print(f"   ❌ Erreur STT: {e}")
        print(f"   📋 Type erreur: {type(e).__name__}")
        
        # Affiche l'erreur complète
        import traceback
        print("\n   📋 Traceback complet:")
        traceback.print_exc()
else:
    print("   ⏭️ Ignoré (pas d'audio TTS)")

# ============================================
# 6. TEST STT avec format webm simulé
# ============================================

print("\n6️⃣ TEST FORMAT WEBM")
print("-" * 40)

if tts_audio:
    try:
        print("   ⏳ Test avec extension .webm...")
        
        audio_file = io.BytesIO(tts_audio)
        audio_file.name = "recording.webm"  # Comme le micro Streamlit
        
        result = client.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1",
            language_code="fra"
        )
        
        if hasattr(result, 'text'):
            print(f"   ✅ Format webm OK: \"{result.text}\"")
        else:
            print(f"   ⚠️ Résultat: {result}")
            
    except Exception as e:
        print(f"   ❌ Erreur format webm: {e}")

# ============================================
# 7. VÉRIFICATION COMPTE ELEVENLABS
# ============================================

print("\n7️⃣ VÉRIFICATION COMPTE")
print("-" * 40)

try:
    # Essaie de récupérer les infos du compte
    user = client.user.get()
    print(f"   ✅ Compte actif")
    
    subscription = client.user.get_subscription()
    if hasattr(subscription, 'character_count'):
        print(f"   📊 Caractères utilisés: {subscription.character_count}")
    if hasattr(subscription, 'character_limit'):
        print(f"   📊 Limite: {subscription.character_limit}")
        
except Exception as e:
    print(f"   ⚠️ Impossible de vérifier le compte: {e}")

# ============================================
# RÉSUMÉ
# ============================================

print("\n" + "=" * 60)
print("   RÉSUMÉ")
print("=" * 60)

print("""
Si TTS ✅ mais STT ❌ :
   → Le problème vient de la fonction STT d'ElevenLabs
   → Solution : Utiliser Groq Whisper (gratuit) pour le STT

Si TTS ❌ et STT ❌ :
   → Problème de crédits ou de clé API
   → Vérifie sur https://elevenlabs.io/app/subscription

Si tout ✅ mais Streamlit ❌ :
   → Le problème vient du format audio du micro
   → Le micro Streamlit envoie du webm qui peut ne pas être compatible
""")

print("=" * 60 + "\n")