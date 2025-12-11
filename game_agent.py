# ============================================
# HERO IA - Game Agent (Logique Backend)
# ============================================
"""
Ce module contient la classe GameAgent qui gère :
- La communication avec l'API Groq
- L'historique des conversations
- Le parsing et la validation des réponses JSON
- La logique anti-troll
- La gestion de l'état du jeu
- LA VALIDATION STRICTE DE L'INVENTAIRE
"""

import os
import json
import re
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from config import (
    LLMConfig, 
    GameConfig, 
    GameTheme, 
    ThemeLibrary,
    DiceRoller,
    GameStatus,
    InputQuality,
    clamp
)


# ============================================
# STRUCTURE DE RÉPONSE
# ============================================

@dataclass
class GameResponse:
    """Structure de données pour une réponse du jeu."""
    
    type: str = "game"
    story: str = ""
    hp_change: int = 0
    game_status: str = "playing"
    input_quality: str = "valid"
    inventory_validated: bool = True
    suggested_actions: List[str] = field(default_factory=lambda: [
        "Observer les alentours",
        "Avancer prudemment",
        "Chercher des indices",
        "Attendre et écouter"
    ])
    scene_description: str = "Lieu mystérieux"
    image_prompt: str = ""  # NOUVEAU
    inventory_add: List[str] = field(default_factory=list)
    inventory_remove: List[str] = field(default_factory=list)
    
    is_error: bool = False
    error_message: str = ""
    raw_response: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GameResponse':
        """Crée une GameResponse depuis un dictionnaire."""
        return cls(
            type=data.get("type", "game"),
            story=data.get("story", ""),
            hp_change=int(data.get("hp_change", 0)),
            game_status=data.get("game_status", "playing"),
            input_quality=data.get("input_quality", "valid"),
            inventory_validated=data.get("inventory_validated", True),
            suggested_actions=data.get("suggested_actions", [])[:4],
            scene_description=data.get("scene_description", "Lieu mystérieux"),
            image_prompt=data.get("image_prompt", ""),  # NOUVEAU
            inventory_add=data.get("inventory_add") or [],
            inventory_remove=data.get("inventory_remove") or []
        )
    
    @classmethod
    def error_response(cls, message: str) -> 'GameResponse':
        """Crée une réponse d'erreur."""
        return cls(
            story=f"*Le fil du destin s'emmêle momentanément...* {message}",
            is_error=True,
            error_message=message,
            suggested_actions=[
                "Réessayer la même action",
                "Faire autre chose",
                "Observer les alentours",
                "Attendre un instant"
            ]
        )


# ============================================
# GAME AGENT - CLASSE PRINCIPALE
# ============================================

class GameAgent:
    """
    Agent principal du jeu gérant l'IA et l'état de la partie.
    
    Attributs:
        client: Client Groq pour les appels API
        model: Modèle LLM utilisé
        system_prompt: Instructions système pour l'IA
        conversation_history: Historique des messages
        current_theme: Thème actuel du jeu
        useless_counter: Compteur d'inputs invalides (anti-troll)
        is_blocked: Flag de blocage (après 3 inputs useless)
        game_started: Indique si le jeu a commencé
    """
    
    def __init__(self, model: str = None):
        """
        Initialise le GameAgent.
        
        Args:
            model: Modèle LLM à utiliser (défaut: config)
        """
        # Charge les variables d'environnement
        load_dotenv()
        
        # Récupère la clé API
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "❌ GROQ_API_KEY non trouvée ! "
                "Créez un fichier .env avec votre clé API."
            )
        
        # Initialise le client Groq
        self.client = Groq(api_key=api_key)
        self.model = model or LLMConfig.DEFAULT_MODEL
        
        # Charge le system prompt
        self.system_prompt = self._load_system_prompt()
        
        # État du jeu
        self.conversation_history: List[Dict[str, str]] = []
        self.current_theme: Optional[GameTheme] = None
        self.useless_counter: int = 0
        self.is_blocked: bool = False
        self.game_started: bool = False
        
        # Stats joueur (gérées par app.py, ici pour référence)
        self.initial_hp: int = GameConfig.INITIAL_HP
        
    def _load_system_prompt(self) -> str:
        """Charge le fichier system_prompt.txt."""
        prompt_path = Path(__file__).parent / "system_prompt.txt"
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Prompt de secours minimal
            return """Tu es un Maître du Jeu de rôle textuel. 
            Réponds UNIQUEMENT en JSON avec les champs: 
            type, story, hp_change, game_status, input_quality, inventory_validated,
            suggested_actions, scene_description, inventory_add, inventory_remove.
            
            RÈGLE ABSOLUE : Le joueur ne peut utiliser QUE les objets listés dans son inventaire.
            Si le joueur tente d'utiliser un objet qu'il n'a pas, refuse de manière immersive."""
    
    def roll_initial_stats(self) -> Dict[str, Any]:
        """
        Lance les dés pour les statistiques initiales.
        
        Returns:
            dict: {'hp': int, 'hp_max': int, 'roll_details': dict}
        """
        roll_result = DiceRoller.roll_with_details(GameConfig.HP_DICE_NOTATION)
        hp = clamp(roll_result['total'], 15, GameConfig.MAX_HP)
        
        return {
            'hp': hp,
            'hp_max': hp,
            'roll_details': roll_result
        }
    
    def initiate_game(self, theme: GameTheme, initial_inventory: List[str] = None) -> GameResponse:
        """
        Démarre une nouvelle partie avec le thème choisi.
        
        Args:
            theme: Le GameTheme sélectionné
            initial_inventory: Liste des objets de départ (optionnel)
            
        Returns:
            GameResponse: La réponse initiale du jeu
        """
        self.current_theme = theme
        self.conversation_history = []
        self.useless_counter = 0
        self.is_blocked = False
        self.game_started = True
        
        # Utilise l'inventaire personnalisé du thème si disponible
        if initial_inventory is None:
            initial_inventory = theme.custom_inventory or list(GameConfig.DEFAULT_INVENTORY)
        
        # Formate l'inventaire pour l'IA
        inventory_str = self._format_inventory_for_ai(initial_inventory)
        
        # Message initial
        initial_message = f"""NOUVEAU JEU - THÈME: {theme.name}

CONTEXTE DE DÉPART:
{theme.initial_context}

═══════════════════════════════════════════════════════════
📦 INVENTAIRE INITIAL DU JOUEUR (LISTE EXACTE ET COMPLÈTE):
{inventory_str}
═══════════════════════════════════════════════════════════

RAPPEL CRITIQUE: Le joueur ne possède QUE ces objets. Rien d'autre.
S'il tente d'utiliser un autre objet, refuse de manière immersive.

Génère maintenant l'introduction immersive du jeu.
Réponds avec type: "init" pour ce premier message.
Plante le décor, mentionne ce que le joueur a sur lui, crée de l'intrigue, et propose 4 premières actions."""

        self.conversation_history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": initial_message}
        ]
        
        return self._call_api()
    
    def step(self, user_input: str, current_inventory: List[str]) -> GameResponse:
        """
        Traite une action du joueur.
        
        Args:
            user_input: L'action/texte du joueur
            current_inventory: L'inventaire ACTUEL du joueur (source de vérité)
            
        Returns:
            GameResponse: La réponse du jeu
        """
        if not self.game_started:
            return GameResponse.error_response("Le jeu n'a pas encore commencé.")
        
        # Nettoie l'input
        user_input = user_input.strip()
        if not user_input:
            return GameResponse.error_response("Veuillez entrer une action.")
        
        # Formate l'inventaire pour l'IA
        inventory_str = self._format_inventory_for_ai(current_inventory)
        
        # Construit le message avec l'inventaire ACTUEL
        message_with_inventory = f"""
═══════════════════════════════════════════════════════════
📦 INVENTAIRE ACTUEL DU JOUEUR (SEULE SOURCE DE VÉRITÉ):
{inventory_str}
═══════════════════════════════════════════════════════════

⚔️ ACTION DU JOUEUR: {user_input}

RAPPEL: Vérifie que le joueur possède bien les objets qu'il mentionne.
S'il tente d'utiliser un objet NON LISTÉ ci-dessus, son action échoue."""
        
        # Ajoute l'input à l'historique
        self.conversation_history.append({
            "role": "user",
            "content": message_with_inventory
        })
        
        # Appelle l'API
        response = self._call_api()
        
        # Gestion anti-troll
        if response.input_quality == "useless":
            self.useless_counter += 1
            if self.useless_counter >= GameConfig.MAX_USELESS_INPUTS:
                self.is_blocked = True
        else:
            # Reset le compteur si input valide
            self.useless_counter = 0
            self.is_blocked = False
        
        return response
    
    def step_with_suggested_action(self, action_text: str, current_inventory: List[str]) -> GameResponse:
        """
        Exécute une action suggérée.
        Les actions suggérées sont toujours valides car générées par l'IA.
        
        Args:
            action_text: Le texte de l'action suggérée
            current_inventory: L'inventaire actuel du joueur
            
        Returns:
            GameResponse: La réponse du jeu
        """
        # Reset le blocage quand on utilise une action suggérée
        self.is_blocked = False
        self.useless_counter = 0
        
        return self.step(action_text, current_inventory)
    
    def _format_inventory_for_ai(self, inventory: List[str]) -> str:
        """
        Formate l'inventaire de manière claire pour l'IA.
        
        Args:
            inventory: Liste des objets
            
        Returns:
            str: Inventaire formaté
        """
        if not inventory:
            return "- (Inventaire vide - le joueur ne possède AUCUN objet)"
        
        formatted_items = []
        for i, item in enumerate(inventory, 1):
            formatted_items.append(f"  {i}. {item}")
        
        return "\n".join(formatted_items) + f"\n\n  TOTAL: {len(inventory)} objet(s)"
    
    def _call_api(self) -> GameResponse:
        """
        Appelle l'API Groq et parse la réponse.
        
        Returns:
            GameResponse: Réponse parsée ou erreur
        """
        try:
            # Appel API avec mode JSON
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                temperature=LLMConfig.TEMPERATURE,
                max_tokens=LLMConfig.MAX_TOKENS,
                top_p=LLMConfig.TOP_P,
                response_format={"type": "json_object"}  # Force JSON
            )
            
            # Récupère le contenu
            raw_content = completion.choices[0].message.content
            
            # Parse le JSON
            response = self._parse_json_response(raw_content)
            
            # Ajoute à l'historique si succès
            if not response.is_error:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": raw_content
                })
            
            return response
            
        except Exception as e:
            error_msg = str(e)
            
            # Gestion des erreurs spécifiques
            if "rate_limit" in error_msg.lower():
                return GameResponse.error_response(
                    "⏳ Trop de requêtes. Attendez quelques secondes..."
                )
            elif "api_key" in error_msg.lower():
                return GameResponse.error_response(
                    "🔑 Clé API invalide. Vérifiez votre fichier .env"
                )
            else:
                return GameResponse.error_response(
                    f"🔌 Erreur de connexion: {error_msg[:100]}"
                )
    
    def _parse_json_response(self, raw_content: str) -> GameResponse:
        """
        Parse et valide la réponse JSON de l'IA.
        
        Args:
            raw_content: Contenu brut de la réponse
            
        Returns:
            GameResponse: Réponse parsée
        """
        try:
            # Nettoie le contenu
            content = raw_content.strip()
            
            # Tente de trouver le JSON si enveloppé dans du markdown
            if "```json" in content:
                match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if match:
                    content = match.group(1)
            elif "```" in content:
                match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
                if match:
                    content = match.group(1)
            
            # Parse le JSON
            data = json.loads(content)
            
            # Valide les champs requis
            response = GameResponse.from_dict(data)
            response.raw_response = raw_content
            
            # Validation des actions suggérées
            if len(response.suggested_actions) < 4:
                # Complète avec des actions par défaut
                default_actions = [
                    "Observer attentivement",
                    "Avancer prudemment",
                    "Chercher une autre voie",
                    "Attendre et réfléchir"
                ]
                while len(response.suggested_actions) < 4:
                    response.suggested_actions.append(
                        default_actions[len(response.suggested_actions)]
                    )
            
            return response
            
        except json.JSONDecodeError as e:
            return GameResponse.error_response(
                f"📜 Erreur de format. Le narrateur reformule..."
            )
        except Exception as e:
            return GameResponse.error_response(
                f"⚠️ Erreur inattendue: {str(e)[:50]}"
            )
    
    def get_conversation_summary(self) -> str:
        """
        Retourne un résumé de la conversation pour debug.
        """
        return f"""
        === État du GameAgent ===
        Modèle: {self.model}
        Thème: {self.current_theme.name if self.current_theme else 'Non défini'}
        Messages: {len(self.conversation_history)}
        Compteur useless: {self.useless_counter}/{GameConfig.MAX_USELESS_INPUTS}
        Bloqué: {self.is_blocked}
        Jeu démarré: {self.game_started}
        """
    
    def reset(self):
        """Réinitialise complètement l'agent."""
        self.conversation_history = []
        self.current_theme = None
        self.useless_counter = 0
        self.is_blocked = False
        self.game_started = False


# ============================================
# TEST DU MODULE
# ============================================

if __name__ == "__main__":
    print("=== Test GameAgent ===")
    
    try:
        agent = GameAgent()
        print("✅ Agent initialisé")
        
        # Test des stats initiales
        stats = agent.roll_initial_stats()
        print(f"📊 Stats initiales: HP = {stats['hp']}/{stats['hp_max']}")
        
        # Test formatage inventaire
        test_inventory = ["Épée rouillée", "Torche", "Corde 10m"]
        print(f"\n📦 Test formatage inventaire:")
        print(agent._format_inventory_for_ai(test_inventory))
        
    except ValueError as e:
        print(f"❌ Erreur: {e}")