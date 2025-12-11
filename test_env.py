# test_full_image.py

import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.cwd() / ".env"
load_dotenv(env_path)

print("\n" + "="*60)
print("   DIAGNOSTIC IMAGE COMPLET")
print("="*60)

# 1. Clé API
api_key = os.getenv("STABILITY_API_KEY")
print(f"\n1️⃣ Clé API: {'✅ Trouvée' if api_key else '❌ Manquante'}")
if api_key:
    print(f"   {api_key[:15]}...")

# 2. Import image_manager
print(f"\n2️⃣ Import image_manager...")
try:
    from image_manager import ImageGenerator, STABILITY_OK
    print(f"   ✅ Importé")
    print(f"   STABILITY_OK = {STABILITY_OK}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    exit()

# 3. Création ImageGenerator
if STABILITY_OK:
    print(f"\n3️⃣ Création ImageGenerator...")
    try:
        gen = ImageGenerator()
        print(f"   ✅ Créé")
        print(f"   Dimensions: {gen.WIDTH}x{gen.HEIGHT}")
        print(f"   Style actuel: {gen.current_style}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        exit()
    
    # 4. Test génération
    print(f"\n4️⃣ Test génération d'image...")
    print(f"   ⏳ Génération en cours (peut prendre 30-60 secondes)...")
    
    try:
        result = gen.generate_image("A brave hero in a dark cave with glowing crystals")
        
        if result.success:
            print(f"   ✅ Image générée!")
            print(f"   Taille base64: {len(result.image_base64)} caractères")
            
            # Sauvegarde
            import base64
            img_data = base64.b64decode(result.image_base64)
            
            output_file = "test_generated_image.png"
            with open(output_file, "wb") as f:
                f.write(img_data)
            
            print(f"   📁 Image sauvegardée: {output_file}")
            print(f"   📏 Taille fichier: {len(img_data)} bytes")
            
        else:
            print(f"   ❌ Échec: {result.error}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

print("\n" + "="*60)
print("Ouvre test_generated_image.png pour voir si l'image existe")
print("="*60 + "\n")