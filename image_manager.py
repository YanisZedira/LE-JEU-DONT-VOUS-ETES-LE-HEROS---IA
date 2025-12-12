

import os
import requests
import base64
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

HUGGINGFACE_OK = False
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if HF_API_KEY:
    HUGGINGFACE_OK = True
    print("✅ Hugging Face (Images) configuré")
else:
    print("⚠️ HUGGINGFACE_API_KEY manquante")


@dataclass
class ImageResult:
    success: bool
    image_base64: Optional[str] = None
    error: Optional[str] = None


class ImageGenerator:
    """Générateur d'images avec Hugging Face (Gratuit)."""
    
    STYLES = {
        "fantasy": "epic fantasy art, magical atmosphere, detailed illustration, high quality",
        "ancient": "ancient egyptian art style, hieroglyphics, golden colors, pharaoh, detailed",
        "space": "sci-fi space art, cosmic, futuristic, stars and nebulas, high quality",
        "victorian": "victorian gothic style, dark manor, candlelight, mysterious, detailed",
        "jungle": "lush jungle environment, tropical, adventure style, exploration, vibrant",
        "dark": "dark underwater scene, deep sea, bioluminescent, mysterious depths, atmospheric",
    }
    
    def __init__(self):
        if not HUGGINGFACE_OK:
            raise ValueError("HUGGINGFACE_API_KEY manquante")
        
        self.api_key = HF_API_KEY
        self.current_style = "fantasy"
        
        
        self.api_url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    
    def set_style(self, style: str):
        if style in self.STYLES:
            self.current_style = style
    
    def generate_image(self, prompt: str) -> ImageResult:
        """Génère une image avec Hugging Face."""
        try:
            if not prompt or len(prompt.strip()) < 5:
                return ImageResult(success=False, error="Prompt trop court")
            
            
            style_suffix = self.STYLES.get(self.current_style, self.STYLES["fantasy"])
            full_prompt = f"{prompt}, {style_suffix}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }
            
            payload = {
                "inputs": full_prompt,
            }
            
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                
                image_bytes = response.content
                
                
                if image_bytes.startswith(b'{') or image_bytes.startswith(b'<'):
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", "Erreur inconnue")
                        return ImageResult(success=False, error=error_msg)
                    except:
                        return ImageResult(success=False, error="Réponse invalide")
                
                
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                
                return ImageResult(success=True, image_base64=image_b64)
                
            elif response.status_code == 503:
                return ImageResult(success=False, error="Modèle en chargement (réessayez dans 30s)")
                
            elif response.status_code == 429:
                return ImageResult(success=False, error="Trop de requêtes (attendez 1 minute)")
                
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", response.text[:150])
                except:
                    error_msg = response.text[:150]
                
                return ImageResult(success=False, error=error_msg)
                
        except requests.Timeout:
            return ImageResult(success=False, error="Timeout - réessayez")
        except Exception as e:
            return ImageResult(success=False, error=str(e)[:100])




if __name__ == "__main__":
    print("\n" + "="*60)
    print("   TEST IMAGE HUGGING FACE (Nouvelle API)")
    print("="*60)
    
    print(f"\nHugging Face: {'✅ OK' if HUGGINGFACE_OK else '❌ Non configuré'}")
    
    if HUGGINGFACE_OK:
        print("\n🧪 Test génération...")
        print("⏳ Peut prendre 30-90 secondes la première fois...")
        
        try:
            gen = ImageGenerator()
            print(f"📡 URL: {gen.api_url}")
            
            result = gen.generate_image("A brave hero standing in a dark cave with glowing crystals")
            
            if result.success:
                print(f"✅ Image générée! ({len(result.image_base64)} chars)")
                
                img_data = base64.b64decode(result.image_base64)
                with open("test_hf_image.png", "wb") as f:
                    f.write(img_data)
                
                print(f"📁 Sauvegardée: test_hf_image.png ({len(img_data)} bytes)")
            else:
                print(f"❌ Erreur: {result.error}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "="*60)