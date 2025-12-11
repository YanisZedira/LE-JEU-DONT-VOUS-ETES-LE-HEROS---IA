# ============================================
# HERO IA - Configuration Centrale
# ============================================
"""
Ce fichier contient toutes les constantes, configurations
et utilitaires du jeu. Architecture Clean Code.

Inclut :
- Configuration LLM (Groq)
- Configuration gameplay
- Thèmes de jeu (scénarios)
- Thèmes visuels (UI/apparence)
- Système de dés
- Énumérations et messages
- Fonctions utilitaires
"""

import random
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


# ============================================
# CONFIGURATION LLM
# ============================================

class LLMConfig:
    """Configuration du modèle de langage."""
    
    # Modèle principal (excellent rapport performance/contexte)
    DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    
    # Modèles alternatifs disponibles
    AVAILABLE_MODELS: List[str] = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile", 
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    
    # Paramètres de génération
    TEMPERATURE: float = 0.85  # Créativité narrative
    MAX_TOKENS: int = 1500     # Longueur max de réponse
    TOP_P: float = 0.9


# ============================================
# CONFIGURATION DU JEU
# ============================================

class GameConfig:
    """Constantes du gameplay."""
    
    # Points de vie
    INITIAL_HP: int = 20
    MAX_HP: int = 30
    MIN_HP: int = 0
    
    # Système anti-troll
    MAX_USELESS_INPUTS: int = 3
    
    # Dés pour stats initiales
    HP_DICE_NOTATION: str = "3d6+10"  # Lance 3d6 et ajoute 10
    
    # Inventaire initial par défaut
    DEFAULT_INVENTORY: List[str] = ["Sacoche en cuir", "Gourde d'eau", "Carte ancienne"]


# ============================================
# THÈMES DE JEU (SCÉNARIOS)
# ============================================

@dataclass
class GameTheme:
    """Définition d'un thème de jeu (scénario)."""
    
    id: str
    name: str
    icon: str
    description: str
    initial_context: str
    primary_color: str
    secondary_color: str
    ambient_keywords: List[str] = field(default_factory=list)


class ThemeLibrary:
    """Bibliothèque des thèmes de jeu disponibles."""
    
    THEMES: Dict[str, GameTheme] = {
        "egypt": GameTheme(
            id="egypt",
            name="Égypte Antique",
            icon="🏛️",
            description="Intrigues politiques dans l'Égypte des Pharaons",
            initial_context="""Tu es un émissaire diplomatique arrivant à Memphis, 
            capitale de l'Égypte antique. Le Pharaon Ramsès, roi mortel mais puissant, 
            t'a convoqué pour une mission secrète. Les temples sont des centres de 
            pouvoir politique, les prêtres sont des administrateurs influents. 
            L'architecture monumentale témoigne de la grandeur de cette civilisation.""",
            primary_color="#D4AF37",
            secondary_color="#8B4513",
            ambient_keywords=["désert", "pyramides", "nil", "palais", "sable"]
        ),
        
        "space": GameTheme(
            id="space",
            name="Survie Spatiale",
            icon="🚀",
            description="Seul à bord d'un vaisseau en dérive dans l'espace",
            initial_context="""Tu te réveilles dans le module de cryogénie du vaisseau 
            cargo 'Odyssey-7'. Les alarmes clignotent en rouge. L'ordinateur de bord 
            t'informe que l'équipage a disparu et que les réserves d'oxygène sont 
            critiques. Tu es seul, perdu dans le secteur non cartographié Zeta-9. 
            Chaque décision compte pour ta survie.""",
            primary_color="#00FFAA",
            secondary_color="#1a1a2e",
            ambient_keywords=["vaisseau", "étoiles", "module", "console", "vide"]
        ),
        
        "manor": GameTheme(
            id="manor",
            name="Manoir Victorien",
            icon="🏚️",
            description="Enquête dans un manoir mystérieux de l'ère victorienne",
            initial_context="""Londres, 1888. Tu es détective privé, convoqué au 
            Manoir Blackwood suite à la disparition du Lord. Le majordome t'accueille 
            sous une pluie battante. Le manoir est immense, ses couloirs sombres 
            cachent des secrets. Les domestiques murmurent, la famille se déchire 
            pour l'héritage. À toi de découvrir la vérité.""",
            primary_color="#8B0000",
            secondary_color="#2F2F2F",
            ambient_keywords=["brouillard", "chandelier", "bibliothèque", "portrait", "pluie"]
        ),
        
        "jungle": GameTheme(
            id="jungle",
            name="Expédition Jungle",
            icon="🌿",
            description="Exploration archéologique en jungle amazonienne",
            initial_context="""1923. Tu es archéologue, au cœur de la jungle amazonienne. 
            Ton guide vient de fuir, emportant les provisions. Devant toi, les ruines 
            d'une cité perdue émergent de la végétation. Les pièges des anciens bâtisseurs 
            sont encore actifs. La faune est hostile. Tu as ta machette, ton journal, 
            et ta détermination.""",
            primary_color="#228B22",
            secondary_color="#8B4513",
            ambient_keywords=["lianes", "ruines", "rivière", "perroquet", "brume"]
        ),
        
        "submarine": GameTheme(
            id="submarine",
            name="Abysses Sous-Marines",
            icon="🌊",
            description="Exploration des profondeurs océaniques mystérieuses",
            initial_context="""Tu es commandant du sous-marin de recherche 'Nautilus II'. 
            À 3000 mètres de profondeur, tu explores une faille océanique inconnue. 
            Le sonar détecte des structures artificielles impossibles. La pression 
            est immense, l'obscurité totale. Tes instruments captent des signaux 
            inexplicables venant des abysses.""",
            primary_color="#000080",
            secondary_color="#20B2AA",
            ambient_keywords=["profondeur", "pression", "lueur", "coque", "silence"]
        )
    }
    
    @classmethod
    def get_theme(cls, theme_id: str) -> Optional[GameTheme]:
        """Récupère un thème par son ID."""
        return cls.THEMES.get(theme_id)
    
    @classmethod
    def get_random_theme(cls) -> GameTheme:
        """Retourne un thème aléatoire."""
        return random.choice(list(cls.THEMES.values()))
    
    @classmethod
    def get_all_themes(cls) -> List[GameTheme]:
        """Retourne tous les thèmes disponibles."""
        return list(cls.THEMES.values())


# ============================================
# THÈMES VISUELS (UI / APPARENCE)
# ============================================

@dataclass
class VisualTheme:
    """Définition d'un thème visuel pour l'interface."""
    
    id: str
    name: str
    icon: str
    description: str
    
    # Couleurs principales
    bg_primary: str
    bg_secondary: str
    bg_card: str
    
    # Texte
    text_primary: str
    text_secondary: str
    text_muted: str
    
    # Accents
    accent_primary: str
    accent_secondary: str
    accent_success: str
    accent_danger: str
    accent_warning: str
    
    # Bordures et ombres
    border_color: str
    shadow_color: str
    
    # Message narrateur
    narrator_bg: str
    narrator_border: str
    narrator_text: str
    
    # Message joueur
    player_bg: str
    player_border: str
    player_text: str
    
    # Options spéciales
    is_dark: bool = True
    background_image: str = ""  # Flag spécial pour fond personnalisé


class VisualThemeLibrary:
    """Bibliothèque des thèmes visuels disponibles."""
    
    THEMES: Dict[str, VisualTheme] = {
        
        # ========== THÈME SOMBRE (Défaut) ==========
        "dark": VisualTheme(
            id="dark",
            name="Sombre",
            icon="🌙",
            description="Mode sombre élégant",
            
            bg_primary="#0a0a0f",
            bg_secondary="#12121a",
            bg_card="#16161f",
            
            text_primary="#f0f0f5",
            text_secondary="#a0a0b0",
            text_muted="#606070",
            
            accent_primary="#d4af37",
            accent_secondary="#8b5cf6",
            accent_success="#22c55e",
            accent_danger="#ef4444",
            accent_warning="#f59e0b",
            
            border_color="rgba(255, 255, 255, 0.08)",
            shadow_color="rgba(0, 0, 0, 0.5)",
            
            narrator_bg="linear-gradient(135deg, #16161f 0%, #1a1a25 100%)",
            narrator_border="#d4af37",
            narrator_text="#f0f0f5",
            
            player_bg="rgba(0, 255, 170, 0.08)",
            player_border="#00ffaa",
            player_text="#a0a0b0",
            
            is_dark=True,
            background_image=""
        ),
        
        # ========== THÈME CLAIR ==========
        "light": VisualTheme(
            id="light",
            name="Clair",
            icon="☀️",
            description="Mode lumineux classique",
            
            bg_primary="#f8f9fa",
            bg_secondary="#ffffff",
            bg_card="#ffffff",
            
            text_primary="#1a1a2e",
            text_secondary="#4a4a5a",
            text_muted="#8a8a9a",
            
            accent_primary="#6366f1",
            accent_secondary="#8b5cf6",
            accent_success="#16a34a",
            accent_danger="#dc2626",
            accent_warning="#d97706",
            
            border_color="rgba(0, 0, 0, 0.1)",
            shadow_color="rgba(0, 0, 0, 0.1)",
            
            narrator_bg="linear-gradient(135deg, #f0f0f5 0%, #e8e8f0 100%)",
            narrator_border="#6366f1",
            narrator_text="#1a1a2e",
            
            player_bg="rgba(99, 102, 241, 0.08)",
            player_border="#6366f1",
            player_text="#4a4a5a",
            
            is_dark=False,
            background_image=""
        ),
        
        # ========== THÈME VERT MODERNE ==========
        "green_modern": VisualTheme(
            id="green_modern",
            name="Vert Moderne",
            icon="💚",
            description="Style tech futuriste",
            
            bg_primary="#f0fdf4",
            bg_secondary="#ffffff",
            bg_card="#ffffff",
            
            text_primary="#14532d",
            text_secondary="#166534",
            text_muted="#4ade80",
            
            accent_primary="#22c55e",
            accent_secondary="#10b981",
            accent_success="#16a34a",
            accent_danger="#dc2626",
            accent_warning="#d97706",
            
            border_color="rgba(34, 197, 94, 0.2)",
            shadow_color="rgba(34, 197, 94, 0.15)",
            
            narrator_bg="linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)",
            narrator_border="#22c55e",
            narrator_text="#14532d",
            
            player_bg="rgba(34, 197, 94, 0.1)",
            player_border="#10b981",
            player_text="#166534",
            
            is_dark=False,
            background_image=""
        ),
        
        # ========== THÈME LIVRE / PARCHEMIN ==========
        "book": VisualTheme(
            id="book",
            name="Livre Ancien",
            icon="📖",
            description="Style livre dont vous êtes le héros",
            
            bg_primary="#f4e4c1",
            bg_secondary="#faf3e0",
            bg_card="#fff8e7",
            
            text_primary="#3d2914",
            text_secondary="#5c4033",
            text_muted="#8b7355",
            
            accent_primary="#8b4513",
            accent_secondary="#a0522d",
            accent_success="#228b22",
            accent_danger="#8b0000",
            accent_warning="#cd853f",
            
            border_color="rgba(139, 69, 19, 0.3)",
            shadow_color="rgba(61, 41, 20, 0.2)",
            
            narrator_bg="linear-gradient(135deg, #fff8e7 0%, #f4e4c1 100%)",
            narrator_border="#8b4513",
            narrator_text="#3d2914",
            
            player_bg="rgba(139, 69, 19, 0.08)",
            player_border="#a0522d",
            player_text="#5c4033",
            
            is_dark=False,
            background_image="book_texture"
        ),
        
        # ========== THÈME CYBER NÉON ==========
        "cyber": VisualTheme(
            id="cyber",
            name="Cyber Néon",
            icon="🌃",
            description="Ambiance cyberpunk néon",
            
            bg_primary="#0f0f1a",
            bg_secondary="#1a1a2e",
            bg_card="#1f1f35",
            
            text_primary="#e0e0ff",
            text_secondary="#a0a0cc",
            text_muted="#6060aa",
            
            accent_primary="#ff00ff",
            accent_secondary="#00ffff",
            accent_success="#00ff88",
            accent_danger="#ff0055",
            accent_warning="#ffaa00",
            
            border_color="rgba(255, 0, 255, 0.2)",
            shadow_color="rgba(255, 0, 255, 0.3)",
            
            narrator_bg="linear-gradient(135deg, #1a1a2e 0%, #2a1a3e 100%)",
            narrator_border="#ff00ff",
            narrator_text="#e0e0ff",
            
            player_bg="rgba(0, 255, 255, 0.1)",
            player_border="#00ffff",
            player_text="#a0a0cc",
            
            is_dark=True,
            background_image=""
        )
    }
    
    @classmethod
    def get_theme(cls, theme_id: str) -> VisualTheme:
        """Récupère un thème par son ID. Retourne le thème sombre par défaut si non trouvé."""
        return cls.THEMES.get(theme_id, cls.THEMES["dark"])
    
    @classmethod
    def get_all_themes(cls) -> List[VisualTheme]:
        """Retourne tous les thèmes visuels disponibles."""
        return list(cls.THEMES.values())
    
    @classmethod
    def get_default_theme(cls) -> VisualTheme:
        """Retourne le thème par défaut (sombre)."""
        return cls.THEMES["dark"]
    
    @classmethod
    def get_theme_ids(cls) -> List[str]:
        """Retourne la liste des IDs de thèmes disponibles."""
        return list(cls.THEMES.keys())


# ============================================
# CONFIGURATION AUDIO (STT / TTS)
# ============================================

@dataclass
class VoiceProfile:
    """Profil de voix pour le TTS."""
    
    id: str
    name: str
    voice_id: str  # ID Edge TTS
    language: str
    gender: str
    description: str
    icon: str


# ============================================
# CONFIGURATION AUDIO - ELEVENLABS
# ============================================

@dataclass
class VoiceProfile:
    """Profil de voix ElevenLabs."""
    
    id: str
    name: str
    voice_id: str  # ID ElevenLabs
    description: str
    icon: str
    style: str  # ex: "narrateur", "mystérieux", etc.


class AudioConfig:
    """Configuration des fonctionnalités audio ElevenLabs."""
    
    # ===== MODÈLES ELEVENLABS =====
    STT_MODEL: str = "scribe_v1"           # Speech-to-Text
    TTS_MODEL: str = "eleven_flash_v2_5"   # Text-to-Speech (rapide)
    TTS_MODEL_HD: str = "eleven_multilingual_v2"  # TTS haute qualité
    
    # ===== LANGUE =====
    LANGUAGE: str = "fra"
    
    # ===== VOIX DISPONIBLES =====
    # Vous pouvez ajouter vos propres voix clonées ici
    VOICES: Dict[str, VoiceProfile] = {
        "narrateur": VoiceProfile(
            id="narrateur",
            name="Le Narrateur",
            voice_id="pNInz6obpgDQGcFmaJgB",  # Adam - voix grave narrative
            description="Voix masculine grave et immersive",
            icon="🎭",
            style="narrateur"
        ),
        "mystere": VoiceProfile(
            id="mystere",
            name="Voix Mystérieuse",
            voice_id="VR6AewLTigWG4xSOukaG",  # Arnold - grave mystérieux
            description="Ton mystérieux et intrigant",
            icon="🌙",
            style="mystérieux"
        ),
        "sage": VoiceProfile(
            id="sage",
            name="Le Sage",
            voice_id="ODq5zmih8GrVes37Dizd",  # Patrick - sage mature
            description="Voix mature et sage",
            icon="📖",
            style="sage"
        ),
        "aventurier": VoiceProfile(
            id="aventurier",
            name="L'Aventurier",
            voice_id="ZQe5CZNOzWyzPSCn5a3c",  # James - dynamique
            description="Voix dynamique et aventurière",
            icon="⚔️",
            style="aventurier"
        ),
        "conteur": VoiceProfile(
            id="conteur",
            name="La Conteuse",
            voice_id="EXAVITQu4vr4xnSDxMaL",  # Bella - voix féminine douce
            description="Voix féminine chaleureuse",
            icon="✨",
            style="conteur"
        )
    }
    
    # ===== PARAMÈTRES PAR DÉFAUT =====
    DEFAULT_VOICE: str = "narrateur"
    TTS_ENABLED_DEFAULT: bool = False
    STT_ENABLED_DEFAULT: bool = False
    
    # ===== PARAMÈTRES TTS =====
    TTS_STABILITY: float = 0.5
    TTS_SIMILARITY: float = 0.75
    TTS_STYLE: float = 0.0
    
    # ===== PARAMÈTRES STT =====
    MAX_AUDIO_DURATION: int = 30  # Secondes
    
    @classmethod
    def get_voice(cls, voice_id: str) -> VoiceProfile:
        """Récupère un profil de voix par son ID."""
        return cls.VOICES.get(voice_id, cls.VOICES[cls.DEFAULT_VOICE])
    
    @classmethod
    def get_all_voices(cls) -> List[VoiceProfile]:
        """Retourne toutes les voix disponibles."""
        return list(cls.VOICES.values())
    
    @classmethod
    def get_voice_ids(cls) -> List[str]:
        """Retourne tous les IDs de voix."""
        return list(cls.VOICES.keys())

# ============================================
# SYSTÈME DE DÉS
# ============================================

class DiceRoller:
    """Utilitaire pour lancer les dés avec notation standard (ex: 3d6+5)."""
    
    # Pattern regex pour parser la notation (ex: "3d6+5", "2d10-2", "1d20")
    DICE_PATTERN = re.compile(r'^(\d+)d(\d+)([+-]\d+)?$')
    
    @classmethod
    def roll(cls, notation: str) -> int:
        """
        Lance les dés selon la notation donnée.
        
        Args:
            notation: Format "XdY+Z" (ex: "3d6+10")
                     X = nombre de dés
                     Y = nombre de faces
                     Z = modificateur (optionnel)
        
        Returns:
            int: Résultat total du lancer
            
        Raises:
            ValueError: Si la notation est invalide
        """
        notation = notation.strip().lower()
        match = cls.DICE_PATTERN.match(notation)
        
        if not match:
            raise ValueError(f"Notation de dés invalide: '{notation}'")
        
        num_dice = int(match.group(1))
        num_faces = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        # Lance chaque dé
        rolls = [random.randint(1, num_faces) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        
        return max(1, total)  # Minimum 1
    
    @classmethod
    def roll_with_details(cls, notation: str) -> Dict[str, Any]:
        """
        Lance les dés et retourne les détails du lancer.
        
        Args:
            notation: Format "XdY+Z"
        
        Returns:
            dict: {
                'notation': str,
                'rolls': List[int],
                'modifier': int,
                'total': int
            }
        """
        notation = notation.strip().lower()
        match = cls.DICE_PATTERN.match(notation)
        
        if not match:
            raise ValueError(f"Notation de dés invalide: '{notation}'")
        
        num_dice = int(match.group(1))
        num_faces = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        rolls = [random.randint(1, num_faces) for _ in range(num_dice)]
        total = max(1, sum(rolls) + modifier)
        
        return {
            'notation': notation,
            'rolls': rolls,
            'modifier': modifier,
            'total': total
        }


# ============================================
# ÉNUMÉRATIONS D'ÉTAT
# ============================================

class GameStatus(Enum):
    """États possibles du jeu."""
    MENU = "menu"
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"
    PAUSED = "paused"


class InputQuality(Enum):
    """Qualité de l'input joueur évaluée par l'IA."""
    VALID = "valid"
    USELESS = "useless"
    BLOCKED = "blocked"


# ============================================
# MESSAGES SYSTÈME
# ============================================

class SystemMessages:
    """Messages affichés à l'utilisateur."""
    
    WELCOME_TITLE = "⚔️ HERO IA"
    WELCOME_SUBTITLE = "Le Jeu de Rôle Textuel Infini"
    
    GAME_OVER = "💀 GAME OVER"
    GAME_OVER_MESSAGE = "Votre aventure s'achève ici... Mais tout héros peut renaître."
    
    VICTORY = "🏆 VICTOIRE"
    VICTORY_MESSAGE = "Vous avez accompli votre quête ! L'histoire chantera vos exploits."
    
    BLOCKED_WARNING = """⚠️ **Le destin force votre main.**  
    Vos divagations ont troublé le fil narratif.  
    Vous devez choisir une action suggérée pour continuer."""
    
    API_ERROR = "🔌 Erreur de connexion. Le destin hésite... Réessayez."
    JSON_ERROR = "📜 Le narrateur s'est emmêlé. Réessayez votre action."
    
    LOADING = "Le destin tisse votre histoire..."


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def clamp(value: int, min_val: int, max_val: int) -> int:
    """Limite une valeur entre un minimum et un maximum."""
    return max(min_val, min(value, max_val))


def get_hp_color(current_hp: int, max_hp: int) -> str:
    """Retourne une couleur HEX basée sur le pourcentage de vie."""
    if max_hp <= 0:
        return "#FF0000"
    
    percentage = (current_hp / max_hp) * 100
    
    if percentage > 70:
        return "#00FF00"  # Vert - Bonne santé
    elif percentage > 40:
        return "#FFD700"  # Or - Attention
    elif percentage > 20:
        return "#FF8C00"  # Orange - Danger
    else:
        return "#FF0000"  # Rouge - Critique


def get_hp_status_text(current_hp: int, max_hp: int) -> str:
    """Retourne un texte de statut basé sur les PV."""
    if max_hp <= 0:
        return "💀 Mort"
    
    percentage = (current_hp / max_hp) * 100
    
    if percentage > 80:
        return "💚 En pleine forme"
    elif percentage > 60:
        return "💛 Légèrement blessé"
    elif percentage > 40:
        return "🧡 Blessé"
    elif percentage > 20:
        return "❤️ Gravement blessé"
    else:
        return "🖤 Mourant"


# ============================================
# TEST DU MODULE
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("HERO IA - Test du module config.py")
    print("=" * 50)
    
    # Test DiceRoller
    print("\n=== Test DiceRoller ===")
    print(f"3d6+10 = {DiceRoller.roll('3d6+10')}")
    details = DiceRoller.roll_with_details('2d10+5')
    print(f"Détails 2d10+5: {details}")
    
    # Test Thèmes de Jeu
    print("\n=== Test Thèmes de Jeu ===")
    for theme in ThemeLibrary.get_all_themes():
        print(f"  {theme.icon} {theme.name}")
    
    # Test Thèmes Visuels
    print("\n=== Test Thèmes Visuels ===")
    for theme in VisualThemeLibrary.get_all_themes():
        mode = "🌙 Sombre" if theme.is_dark else "☀️ Clair"
        special = " (avec texture)" if theme.background_image else ""
        print(f"  {theme.icon} {theme.name} - {mode}{special}")
    
    # Test Couleurs HP
    print("\n=== Test Couleurs HP ===")
    for hp in [20, 15, 10, 5, 2]:
        color = get_hp_color(hp, 20)
        status = get_hp_status_text(hp, 20)
        print(f"  HP {hp}/20: {color} - {status}")
    
    print("\n" + "=" * 50)
    print("✅ Tous les tests passés !")
    print("=" * 50)