import streamlit as st
from typing import Optional
import re
import time

from config import (
    GameConfig, ThemeLibrary, GameTheme, SystemMessages,
    get_hp_color, get_hp_status_text, clamp,
    VisualThemeLibrary,
)
from game_agent import GameAgent, GameResponse

AUDIO_OK = False
AudioManager = None
try:
    from audio_manager import AudioManager as AM, GTTS_OK
    if GTTS_OK:
        AudioManager = AM
        AUDIO_OK = True
except:
    pass

IMAGE_OK = False
ImageGenerator = None
try:
    from image_manager import ImageGenerator as IG, HUGGINGFACE_OK
    if HUGGINGFACE_OK:
        ImageGenerator = IG
        IMAGE_OK = True
except:
    pass

MIC_OK = False
mic_recorder = None
try:
    from streamlit_mic_recorder import mic_recorder as mr
    mic_recorder = mr
    MIC_OK = True
except:
    pass

VOICE_UI_OK = False
try:
    from voice_ui import inject_voice_css, show_ai_speaking, show_transcription, show_voice_mode_badge
    VOICE_UI_OK = True
except:
    pass



st.set_page_config(
    page_title="HERO IA",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_state():
    defaults = {
        'visual_theme': 'dark',
        'agent': None,
        'game_active': False,
        'game_over': False,
        'victory': False,
        'hp': 20,
        'hp_max': 20,
        'inventory': [],
        'history': [],  # Maintenant contient {'content': str, 'narrator': bool, 'image': str ou None}
        'actions': [],
        'scene': '',
        'game_theme': None,
        'audio_mgr': None,
        'voice_mode': False,
        'voice_key': 'fr',
        'audio_to_play': None,
        'image_gen': None,
        'images_enabled': True,
        'mic_counter': 0,
        'last_audio_id': None,
    }
    
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    
    if AUDIO_OK and st.session_state.audio_mgr is None:
        try:
            st.session_state.audio_mgr = AudioManager()
        except:
            pass
    
    if IMAGE_OK and st.session_state.image_gen is None:
        try:
            st.session_state.image_gen = ImageGenerator()
        except:
            pass

# ============================================
# CSS
# ============================================

def load_css():
    theme = VisualThemeLibrary.get_theme(st.session_state.visual_theme)
    
    st.markdown(f"""
    <style>
        :root {{
            --bg: {theme.bg_primary};
            --bg2: {theme.bg_secondary};
            --card: {theme.bg_card};
            --text: {theme.text_primary};
            --text2: {theme.text_secondary};
            --muted: {theme.text_muted};
            --accent: {theme.accent_primary};
            --accent2: {theme.accent_secondary};
        }}
        
        .stApp {{ background: var(--bg); }}
        #MainMenu, footer, header {{ visibility: hidden; }}
        
        /* Narrateur */
        .narrator {{
            background: var(--card);
            border-left: 4px solid var(--accent);
            border-radius: 0 16px 16px 0;
            padding: 1.5rem;
            margin: 1rem 0;
            color: var(--text);
            line-height: 1.9;
        }}
        .narrator p {{ margin-bottom: 1rem; }}
        .narrator p:last-child {{ margin-bottom: 0; }}
        
        /* Joueur */
        .player {{
            background: rgba(139, 92, 246, 0.1);
            border-left: 4px solid var(--accent2);
            border-radius: 0 12px 12px 0;
            padding: 1rem 1.5rem;
            margin: 0.8rem 0;
            color: var(--text2);
        }}
        
        /* Badge scène */
        .scene-badge {{
            display: inline-block;
            background: rgba(139, 92, 246, 0.12);
            border: 1px solid rgba(139, 92, 246, 0.25);
            border-radius: 25px;
            padding: 0.4rem 1rem;
            font-size: 0.85rem;
            color: var(--accent2);
            margin-bottom: 1rem;
        }}
        
        /* Section title */
        .section-title {{
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--muted);
            margin-bottom: 0.5rem;
        }}
        
        /* HP */
        .hp-box {{
            background: var(--card);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        .hp-bar {{
            background: rgba(100,100,100,0.3);
            border-radius: 20px;
            height: 20px;
            overflow: hidden;
        }}
        .hp-fill {{
            height: 100%;
            border-radius: 20px;
            transition: width 0.4s;
        }}
        .hp-fill.high {{ background: linear-gradient(90deg, #22c55e, #4ade80); }}
        .hp-fill.mid {{ background: linear-gradient(90deg, #f59e0b, #fbbf24); }}
        .hp-fill.low {{ background: linear-gradient(90deg, #f97316, #fb923c); }}
        .hp-fill.crit {{ background: linear-gradient(90deg, #ef4444, #f87171); animation: pulse 1s infinite; }}
        @keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.6; }} }}
        .hp-label {{ text-align: center; margin-top: 0.5rem; font-weight: 600; }}
        
        /* Inventaire */
        .inv-item {{
            background: var(--bg2);
            border-left: 3px solid var(--accent);
            border-radius: 6px;
            padding: 0.5rem 0.75rem;
            margin: 0.25rem 0;
            font-size: 0.9rem;
            color: var(--text);
        }}
        
        /* Theme cards */
        .theme-card {{
            background: var(--card);
            border: 1px solid var(--muted);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            margin-bottom: 0.5rem;
        }}
        .theme-icon {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .theme-name {{ font-weight: 600; color: var(--text); }}
        .theme-desc {{ font-size: 0.85rem; color: var(--muted); margin-top: 0.3rem; }}
        
        /* ========================================
           IMAGE SIDEBAR (Side-by-Side)
           ======================================== */
        
        .image-sidebar {{
            position: sticky;
            top: 20px;
            padding: 8px;
            background: var(--card);
            border: 2px solid var(--accent);
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        
        .sidebar-image {{
            width: 100%;
            height: auto;
            max-height: 400px;
            object-fit: cover;
            border-radius: 8px;
            display: block;
        }}
        
        /* Responsive : si écran petit, empile verticalement */
        @media (max-width: 768px) {{
            .sidebar-image {{
                max-height: 250px;
            }}
        }}
        
        /* Zone micro */
        .mic-zone {{
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%);
            border: 2px dashed rgba(139, 92, 246, 0.3);
            border-radius: 20px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        }}
        
        /* Save success */
        .save-success {{
            background: rgba(34, 197, 94, 0.15);
            border: 2px solid #22c55e;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            text-align: center;
            color: #22c55e;
            font-weight: 600;
            animation: fadeIn 0.3s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
    """, unsafe_allow_html=True)
    
    if VOICE_UI_OK:
        inject_voice_css()

# ============================================
# UTILS
# ============================================

def fmt_story(text: str) -> str:
    if not text:
        return ""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    paras, current = [], []
    for s in sentences:
        current.append(s)
        if len(current) >= 2 or '"' in s or '«' in s:
            paras.append(' '.join(current))
            current = []
    if current:
        paras.append(' '.join(current))
    return ''.join(f'<p>{p}</p>' for p in paras if p.strip())

# ============================================
# AUDIO
# ============================================

def speak(text: str):
    if not st.session_state.voice_mode or not st.session_state.audio_mgr:
        return
    if not text or len(text.strip()) < 5:
        return
    try:
        result = st.session_state.audio_mgr.text_to_speech(text)
        if result.success and result.audio_bytes:
            st.session_state.audio_to_play = result.audio_bytes
    except:
        pass


def play_audio():
    if not st.session_state.audio_to_play:
        return
    if VOICE_UI_OK:
        show_ai_speaking()
    st.audio(st.session_state.audio_to_play, format="audio/mp3", autoplay=True)
    st.session_state.audio_to_play = None


def transcribe(audio_bytes: bytes) -> Optional[str]:
    if not st.session_state.audio_mgr:
        return None
    try:
        result = st.session_state.audio_mgr.speech_to_text(audio_bytes)
        return result.text if result.success else None
    except:
        return None

# ============================================
# IMAGE
# ============================================

def generate_image(prompt: str, theme_id: str = None) -> Optional[str]:
    """Génère une image et retourne le base64."""
    if not st.session_state.images_enabled or not st.session_state.image_gen:
        return None
    if not prompt or len(prompt.strip()) < 5:
        return None
    try:
        gen = st.session_state.image_gen
        if theme_id:
            style_map = {
                "orient_express": "fantasy",
                "egypt": "ancient",
                "space": "space",
                "manor": "victorian",
                "jungle": "jungle",
                "submarine": "dark",
            }
            gen.set_style(style_map.get(theme_id, "fantasy"))
        result = gen.generate_image(prompt)
        if result.success and result.image_base64:
            return result.image_base64
    except:
        pass
    return None

# ============================================
# UI COMPONENTS
# ============================================

# ============================================
# UI COMPONENTS (Mise à jour Side-by-Side)
# ============================================

def show_hp():
    hp, mx = st.session_state.hp, st.session_state.hp_max
    pct = (hp/mx*100) if mx > 0 else 0
    cls = "high" if pct > 70 else "mid" if pct > 40 else "low" if pct > 20 else "crit"
    st.markdown(f"""
    <div class="hp-box">
        <div class="section-title">❤️ Points de Vie</div>
        <div class="hp-bar"><div class="hp-fill {cls}" style="width:{pct}%"></div></div>
        <div class="hp-label" style="color:{get_hp_color(hp,mx)}">{hp}/{mx} — {get_hp_status_text(hp,mx)}</div>
    </div>
    """, unsafe_allow_html=True)


def show_inv():
    inv = st.session_state.inventory
    st.markdown('<div class="section-title">🎒 Inventaire</div>', unsafe_allow_html=True)
    if inv:
        for item in inv:
            st.markdown(f'<div class="inv-item">• {item}</div>', unsafe_allow_html=True)
    else:
        st.caption("Vide")


def show_narrator(content: str, image_b64: Optional[str] = None):
    """
    Affiche le message du narrateur avec image optionnelle en side-by-side.
    
    - Si image présente : colonnes [3, 1] (texte à gauche, image à droite)
    - Si pas d'image : texte sur toute la largeur
    """
    if image_b64:
        # Mode Side-by-Side avec colonnes
        col_text, col_img = st.columns([3, 1])
        
        with col_text:
            st.markdown(f'<div class="narrator">{fmt_story(content)}</div>', unsafe_allow_html=True)
        
        with col_img:
            st.markdown(f"""
            <div class="image-sidebar">
                <img src="data:image/png;base64,{image_b64}" class="sidebar-image" alt="Illustration" />
            </div>
            """, unsafe_allow_html=True)
    else:
        # Mode pleine largeur sans image
        st.markdown(f'<div class="narrator">{fmt_story(content)}</div>', unsafe_allow_html=True)


def show_player(content: str):
    st.markdown(f'<div class="player"><strong>⚔️ Vous:</strong> {content}</div>', unsafe_allow_html=True)


def add_msg(content: str, narrator: bool = True, image_b64: Optional[str] = None):
    """Ajoute un message à l'historique avec image optionnelle."""
    st.session_state.history.append({
        'content': content,
        'narrator': narrator,
        'image': image_b64
    })

# ============================================
# SIDEBAR
# ============================================

def show_voice_controls():
    st.markdown('<div class="section-title">🎙️ Mode Vocal</div>', unsafe_allow_html=True)
    
    if not AUDIO_OK:
        st.warning("⚠️ Audio non configuré")
        return
    if not MIC_OK:
        st.warning("⚠️ Micro non disponible")
        return
    
    voice_on = st.toggle("Activer", value=st.session_state.voice_mode, key="voice_toggle")
    if voice_on != st.session_state.voice_mode:
        st.session_state.voice_mode = voice_on
        st.rerun()
    
    if st.session_state.voice_mode and VOICE_UI_OK:
        show_voice_mode_badge(True)
        
        voices = AudioManager.get_voices()
        names = [v["name"] for v in voices]
        keys = [v["key"] for v in voices]
        idx = keys.index(st.session_state.voice_key) if st.session_state.voice_key in keys else 0
        
        selected = st.selectbox("Voix", names, index=idx, key="voice_sel", label_visibility="collapsed")
        new_key = keys[names.index(selected)]
        if new_key != st.session_state.voice_key:
            st.session_state.voice_key = new_key
            if st.session_state.audio_mgr:
                st.session_state.audio_mgr.set_voice(new_key)
    
    st.markdown("---")


def show_image_controls():
    st.markdown('<div class="section-title">🖼️ Images</div>', unsafe_allow_html=True)
    
    if not IMAGE_OK:
        st.caption("⚠️ Images non configurées")
        return
    
    img_on = st.toggle("Générer images", value=st.session_state.images_enabled, key="img_toggle")
    if img_on != st.session_state.images_enabled:
        st.session_state.images_enabled = img_on
        st.rerun()
    
    st.markdown("---")


def show_theme_selector():
    st.markdown('<div class="section-title">🎨 Thème</div>', unsafe_allow_html=True)
    themes = VisualThemeLibrary.get_all_themes()
    current = st.session_state.visual_theme
    cols = st.columns(3)
    for i, t in enumerate(themes):
        with cols[i % 3]:
            if st.button(t.icon, key=f"vt_{t.id}", use_container_width=True,
                        type="primary" if current == t.id else "secondary", help=t.name):
                st.session_state.visual_theme = t.id
                st.rerun()
    st.markdown("---")


def show_sidebar():
    theme = VisualThemeLibrary.get_theme(st.session_state.visual_theme)
    
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; font-size:1.5rem; font-weight:bold; 
            color:{theme.accent_primary}; margin-bottom:15px;">⚔️ HERO IA</div>
        """, unsafe_allow_html=True)
        
        # BOUTON SAUVEGARDER (démo)
        if st.session_state.game_active:
            if st.button("💾 Sauvegarder", use_container_width=True, type="primary"):
                st.session_state['save_message'] = True
                st.rerun()
            
            # Message de sauvegarde
            if st.session_state.get('save_message'):
                st.markdown('<div class="save-success">✅ Partie sauvegardée !</div>', unsafe_allow_html=True)
                time.sleep(2)
                st.session_state['save_message'] = False
        
        st.markdown("---")
        
        show_voice_controls()
        show_image_controls()
        show_theme_selector()
        
        if st.session_state.game_active:
            gt = st.session_state.game_theme
            if gt:
                st.markdown(f"**{gt.icon} {gt.name}**")
            show_hp()
            show_inv()
            st.markdown("---")
            if st.button("🚪 Abandonner", use_container_width=True):
                reset_game()
                st.rerun()
        
        st.markdown("---")
        status = []
        if AUDIO_OK: status.append("🔊")
        if IMAGE_OK: status.append("🖼️")
        if MIC_OK: status.append("🎤")
        st.caption(f"v12 Final • {' '.join(status)}")

# ============================================
# GAME LOGIC
# ============================================

def apply_inv(response: GameResponse):
    if response.inventory_add:
        for item in response.inventory_add:
            if item and item.strip() not in st.session_state.inventory:
                st.session_state.inventory.append(item.strip())
    if response.inventory_remove:
        for item in response.inventory_remove:
            for inv_item in st.session_state.inventory[:]:
                if inv_item.lower() == item.strip().lower():
                    st.session_state.inventory.remove(inv_item)
                    break


def start_game(theme: GameTheme):
    try:
        agent = GameAgent()
        st.session_state.agent = agent
        
        stats = agent.roll_initial_stats()
        st.session_state.hp = stats['hp']
        st.session_state.hp_max = stats['hp_max']
        
        # Utilise l'inventaire personnalisé du thème
        initial_inv = theme.custom_inventory or list(GameConfig.DEFAULT_INVENTORY)
        st.session_state.inventory = list(initial_inv)
        
        st.session_state.history = []
        st.session_state.game_theme = theme
        st.session_state.audio_to_play = None
        st.session_state.mic_counter = 0
        st.session_state.last_audio_id = None
        
        response = agent.initiate_game(theme, initial_inv)
        
        if not response.is_error:
            # Génère l'image
            img_b64 = None
            if st.session_state.images_enabled and IMAGE_OK:
                prompt = getattr(response, 'image_prompt', None) or response.scene_description
                with st.spinner("🎨 Génération..."):
                    img_b64 = generate_image(prompt, theme.id)
            
            # Ajoute avec l'image
            add_msg(response.story, True, img_b64)
            
            st.session_state.actions = response.suggested_actions
            st.session_state.scene = response.scene_description
            st.session_state.game_active = True
            st.session_state.game_over = False
            st.session_state.victory = False
            
            apply_inv(response)
            speak(response.story)
        else:
            st.error(response.error_message)
    except Exception as e:
        st.error(f"Erreur: {e}")


def do_action(action: str, suggested: bool = False):
    if not st.session_state.agent or not st.session_state.game_active:
        return
    
    # Ajoute l'action du joueur (sans image)
    add_msg(action, False, None)
    
    inv = list(st.session_state.inventory)
    
    if suggested:
        response = st.session_state.agent.step_with_suggested_action(action, inv)
    else:
        response = st.session_state.agent.step(action, inv)
    
    if not response.is_error:
        # Génère l'image
        img_b64 = None
        if st.session_state.images_enabled and IMAGE_OK:
            prompt = getattr(response, 'image_prompt', None) or response.scene_description
            img_b64 = generate_image(prompt, st.session_state.game_theme.id if st.session_state.game_theme else None)
        
        # Ajoute la réponse du narrateur avec l'image
        add_msg(response.story, True, img_b64)
        
        if response.hp_change:
            st.session_state.hp = clamp(st.session_state.hp + response.hp_change, 0, st.session_state.hp_max)
        
        if response.input_quality == "valid" and response.inventory_validated:
            apply_inv(response)
        
        st.session_state.actions = response.suggested_actions
        st.session_state.scene = response.scene_description
        st.session_state.mic_counter += 1
        
        speak(response.story)
        
        if response.game_status == "lost" or st.session_state.hp <= 0:
            st.session_state.game_over = True
            st.session_state.game_active = False
        elif response.game_status == "won":
            st.session_state.victory = True
            st.session_state.game_active = False
    else:
        st.error(response.error_message)


def reset_game():
    st.session_state.agent = None
    st.session_state.game_active = False
    st.session_state.game_over = False
    st.session_state.victory = False
    st.session_state.hp = 20
    st.session_state.hp_max = 20
    st.session_state.inventory = []
    st.session_state.history = []
    st.session_state.actions = []
    st.session_state.scene = ''
    st.session_state.game_theme = None
    st.session_state.audio_to_play = None
    st.session_state.mic_counter = 0
    st.session_state.last_audio_id = None

# ============================================
# SCREENS
# ============================================

def screen_welcome():
    theme = VisualThemeLibrary.get_theme(st.session_state.visual_theme)
    
    st.markdown(f"""
    <div style="text-align:center; padding:2rem 0;">
        <h1 style="font-size:3.5rem; margin-bottom:0.5rem;">⚔️ HERO IA</h1>
        <p style="color:{theme.text_secondary}; font-size:1.2rem;">Le Jeu de Rôle Textuel Infini</p>
        <p style="color:{theme.text_muted}; font-size:0.95rem;">
            🎙️ Parlez • 🔊 Écoutez • 🖼️ Visualisez
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎭 Choisissez votre aventure")
    
    themes = ThemeLibrary.get_all_themes()
    cols = st.columns(3)
    
    for i, gt in enumerate(themes):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="theme-card">
                <div class="theme-icon">{gt.icon}</div>
                <div class="theme-name">{gt.name}</div>
                <div class="theme-desc">{gt.description}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Jouer", key=f"play_{gt.id}", use_container_width=True):
                start_game(gt)
                st.rerun()
    
    st.markdown("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🎲 Aventure Aléatoire", use_container_width=True, type="primary"):
            start_game(ThemeLibrary.get_random_theme())
            st.rerun()


def screen_game():
    # Badge scène
    if st.session_state.scene:
        st.markdown(f'<div class="scene-badge">🎬 {st.session_state.scene}</div>', unsafe_allow_html=True)
    
    # Audio
    play_audio()
    
    # Historique avec images intégrées
    for msg in st.session_state.history:
        if msg['narrator']:
            show_narrator(msg['content'], msg.get('image'))
        else:
            show_player(msg['content'])
    
    st.markdown("---")
    
    agent = st.session_state.agent
    blocked = agent.is_blocked if agent else False
    if blocked:
        st.warning(SystemMessages.BLOCKED_WARNING)
    
    # Zone Vocale
    if st.session_state.voice_mode and MIC_OK and not blocked:
        st.markdown("### 🎤 Commande Vocale")
        st.markdown('<div class="mic-zone">', unsafe_allow_html=True)
        st.caption("Cliquez pour parler")
        
        mic_key = f"mic_{st.session_state.mic_counter}"
        audio = mic_recorder(
            start_prompt="🎤 Parler",
            stop_prompt="🛑 Envoyer",
            just_once=False,
            use_container_width=True,
            format="webm",
            key=mic_key
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if audio and audio.get('bytes'):
            audio_id = id(audio['bytes'])
            if audio_id != st.session_state.last_audio_id:
                st.session_state.last_audio_id = audio_id
                
                with st.spinner("🔄 Transcription..."):
                    text = transcribe(audio['bytes'])
                
                if text:
                    if VOICE_UI_OK:
                        show_transcription(text)
                    else:
                        st.success(f'🎤 "{text}"')
                    time.sleep(0.3)
                    do_action(text, suggested=False)
                    st.rerun()
                else:
                    st.error("❌ Transcription échouée")
        
        st.markdown("---")
    
    # Actions
    st.markdown("### 🎯 Actions")
    actions = st.session_state.actions
    if actions:
        cols = st.columns(2)
        for i, act in enumerate(actions[:4]):
            with cols[i % 2]:
                if st.button(f"→ {act}", key=f"act_{i}_{st.session_state.mic_counter}", use_container_width=True):
                    do_action(act, suggested=True)
                    st.rerun()
    
    st.markdown("---")
    
    # Input texte
    if not blocked:
        st.markdown("### ✍️ Taper")
        user_input = st.chat_input("Que faites-vous ?")
        if user_input:
            do_action(user_input, suggested=False)
            st.rerun()


def screen_gameover():
    st.markdown("""
    <div style="text-align:center; padding:3rem 0;">
        <h1 style="font-size:4rem; color:#ef4444;">💀 GAME OVER</h1>
        <p style="color:#a0a0b0;">Votre aventure s'achève...</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.voice_mode and not st.session_state.audio_to_play:
        speak("Game Over.")
    play_audio()
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🔄 Recommencer", use_container_width=True, type="primary"):
            reset_game()
            st.rerun()


def screen_victory():
    st.markdown("""
    <div style="text-align:center; padding:3rem 0;">
        <h1 style="font-size:4rem;">🏆 VICTOIRE !</h1>
        <p style="color:#a0a0b0;">Vous avez accompli votre quête !</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.voice_mode and not st.session_state.audio_to_play:
        speak("Victoire !")
    play_audio()
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🎮 Nouvelle Aventure", use_container_width=True, type="primary"):
            reset_game()
            st.rerun()

# ============================================
# MAIN
# ============================================

def main():
    init_state()
    load_css()
    show_sidebar()
    
    if st.session_state.game_over:
        screen_gameover()
    elif st.session_state.victory:
        screen_victory()
    elif st.session_state.game_active:
        screen_game()
    else:
        screen_welcome()


if __name__ == "__main__":
    main()
