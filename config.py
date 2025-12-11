# ============================================
# HERO IA - Configuration Centrale
# ============================================

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
    
    DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    
    AVAILABLE_MODELS: List[str] = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile", 
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    
    TEMPERATURE: float = 0.85
    MAX_TOKENS: int = 1500
    TOP_P: float = 0.9


# ============================================
# CONFIGURATION DU JEU
# ============================================

class GameConfig:
    """Constantes du gameplay."""
    
    INITIAL_HP: int = 20
    MAX_HP: int = 30
    MIN_HP: int = 0
    MAX_USELESS_INPUTS: int = 3
    HP_DICE_NOTATION: str = "3d6+10"
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
    custom_inventory: Optional[List[str]] = None  # NOUVEAU


class ThemeLibrary:
    """Bibliothèque des thèmes de jeu disponibles."""
    
    THEMES: Dict[str, GameTheme] = {
        
        # ========== NOUVEAU : ORIENT-EXPRESS (DÉMO RAPIDE) ==========
        "orient_express": GameTheme(
            id="orient_express",
            name="Le Crime de l'Orient-Express",
            icon="🚂",
            description="Enquête express dans le train mythique (3 min chrono)",
            initial_context="""**CONTEXTE URGENT - ENQUÊTE CHRONOMÉTRÉE**

📍 **LIEU** : Orient-Express, 1934, quelque part entre Paris et Istanbul
⏰ **TEMPS LIMITE** : Très court - l'enquête doit se résoudre rapidement

🎯 **MISSION** :
Tu es détective privé, appelé en urgence dans le wagon-restaurant. 
Le riche industriel Monsieur Ratchett vient d'être retrouvé MORT dans sa cabine.
Le train est bloqué par une avalanche - le meurtrier est À BORD.

👤 **SUSPECTS** (3 seulement pour aller vite) :
1. **Madame Duval** - Actrice française, visage pâle, mains tremblantes
2. **Colonel Armstrong** - Militaire britannique, rigide, l'air coupable
3. **Giuseppe le Serveur** - Italien nerveux, dernier à avoir vu la victime

🔍 **TU AS EXACTEMENT 4-5 ACTIONS** pour :
- Interroger les suspects (choisis bien qui et quoi demander)
- Fouiller la cabine du mort (indices cruciaux)
- Examiner le corps
- Accuser le coupable

⚠️ **RÈGLES DE LA DÉMO RAPIDE** :
- Chaque action compte, pas de temps à perdre
- Si tu accuses le MAUVAIS suspect = GAME OVER (le vrai tueur te poignarde)
- Si tu trouves le BON coupable avec une preuve = VICTOIRE
- Si tu tardes trop (plus de 6 tours) = Le meurtrier s'échappe = DÉFAITE
- Les indices sont ÉVIDENTS (c'est une démo, pas une vraie enquête complexe)

🎲 **LE MEURTRIER EST** : [L'IA choisira ALÉATOIREMENT entre les 3 suspects au début, avec un indice clair à trouver]

**IMPORTANT POUR L'IA** :
- Choisis IMMÉDIATEMENT (en secret) qui est le meurtrier parmi les 3
- Place UN indice CLAIR dans la cabine OU dans le comportement du coupable
- Si le joueur interroge le bon suspect avec la bonne question = indice évident
- Si le joueur accuse avec preuve = game_status: "won"
- Si le joueur accuse sans preuve ou le mauvais = game_status: "lost"
- Rends ça RAPIDE et INTENSE (descriptions courtes, pas de longueurs)

**ATMOSPHÈRE** : Tension, urgence, mystère, années 30, luxe du train""",
            primary_color="#8B0000",
            secondary_color="#DAA520",
            ambient_keywords=["train", "luxe", "années 30", "mystère", "hiver"],
            custom_inventory=[
                "Carnet de notes",
                "Loupe de détective", 
                "Insigne de détective",
                "Montre à gousset"
            ]
        ),
        
        # ========== THÈMES ORIGINAUX ==========
        
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
        return cls.THEMES.get(theme_id)
    
    @classmethod
    def get_random_theme(cls) -> GameTheme:
        return random.choice(list(cls.THEMES.values()))
    
    @classmethod
    def get_all_themes(cls) -> List[GameTheme]:
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
    bg_primary: str
    bg_secondary: str
    bg_card: str
    text_primary: str
    text_secondary: str
    text_muted: str
    accent_primary: str
    accent_secondary: str
    accent_success: str
    accent_danger: str
    accent_warning: str
    border_color: str
    shadow_color: str
    narrator_bg: str
    narrator_border: str
    narrator_text: str
    player_bg: str
    player_border: str
    player_text: str
    is_dark: bool = True
    background_image: str = ""


class VisualThemeLibrary:
    """Bibliothèque des thèmes visuels disponibles."""
    
    THEMES: Dict[str, VisualTheme] = {
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
            is_dark=True
        ),
        
        "light": VisualTheme(
            id="light",
            name="Clair",
            icon="☀️",
            description="Mode lumineux",
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
            is_dark=False
        ),
        
        "green_modern": VisualTheme(
            id="green_modern",
            name="Vert Moderne",
            icon="💚",
            description="Style tech",
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
            is_dark=False
        ),
    }
    
    @classmethod
    def get_theme(cls, theme_id: str) -> VisualTheme:
        return cls.THEMES.get(theme_id, cls.THEMES["dark"])
    
    @classmethod
    def get_all_themes(cls) -> List[VisualTheme]:
        return list(cls.THEMES.values())


# ============================================
# SYSTÈME DE DÉS
# ============================================

class DiceRoller:
    DICE_PATTERN = re.compile(r'^(\d+)d(\d+)([+-]\d+)?$')
    
    @classmethod
    def roll(cls, notation: str) -> int:
        notation = notation.strip().lower()
        match = cls.DICE_PATTERN.match(notation)
        if not match:
            raise ValueError(f"Notation invalide: '{notation}'")
        num_dice = int(match.group(1))
        num_faces = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        rolls = [random.randint(1, num_faces) for _ in range(num_dice)]
        return max(1, sum(rolls) + modifier)
    
    @classmethod
    def roll_with_details(cls, notation: str) -> Dict[str, Any]:
        notation = notation.strip().lower()
        match = cls.DICE_PATTERN.match(notation)
        if not match:
            raise ValueError(f"Notation invalide: '{notation}'")
        num_dice = int(match.group(1))
        num_faces = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        rolls = [random.randint(1, num_faces) for _ in range(num_dice)]
        return {
            'notation': notation,
            'rolls': rolls,
            'modifier': modifier,
            'total': max(1, sum(rolls) + modifier)
        }


# ============================================
# ÉNUMÉRATIONS
# ============================================

class GameStatus(Enum):
    MENU = "menu"
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"
    PAUSED = "paused"


class InputQuality(Enum):
    VALID = "valid"
    USELESS = "useless"
    BLOCKED = "blocked"


# ============================================
# MESSAGES SYSTÈME
# ============================================

class SystemMessages:
    WELCOME_TITLE = "⚔️ HERO IA"
    WELCOME_SUBTITLE = "Le Jeu de Rôle Textuel Infini"
    GAME_OVER = "💀 GAME OVER"
    GAME_OVER_MESSAGE = "Votre aventure s'achève ici..."
    VICTORY = "🏆 VICTOIRE"
    VICTORY_MESSAGE = "Vous avez accompli votre quête !"
    BLOCKED_WARNING = "⚠️ Le destin force votre main. Choisissez une action suggérée."
    API_ERROR = "🔌 Erreur de connexion..."
    JSON_ERROR = "📜 Le narrateur reformule..."
    LOADING = "Le destin tisse votre histoire..."


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(value, max_val))


def get_hp_color(current_hp: int, max_hp: int) -> str:
    if max_hp <= 0:
        return "#FF0000"
    percentage = (current_hp / max_hp) * 100
    if percentage > 70:
        return "#00FF00"
    elif percentage > 40:
        return "#FFD700"
    elif percentage > 20:
        return "#FF8C00"
    else:
        return "#FF0000"


def get_hp_status_text(current_hp: int, max_hp: int) -> str:
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