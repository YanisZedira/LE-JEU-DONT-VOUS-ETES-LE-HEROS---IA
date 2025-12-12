

import streamlit as st


def inject_voice_css():
    """Injecte le CSS pour l'interface vocale."""
    
    st.markdown("""
    <style>
        /* ================================
           ZONE MICRO
           ================================ */
        .mic-zone {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%);
            border: 2px dashed rgba(139, 92, 246, 0.3);
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
            text-align: center;
        }
        
        .mic-instructions {
            color: #a0a0cc;
            font-size: 0.9rem;
            margin-bottom: 15px;
        }
        
        /* ================================
           INDICATEUR ÉCOUTE
           ================================ */
        .listening-box {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px 24px;
            background: rgba(239, 68, 68, 0.1);
            border-radius: 30px;
            border: 1px solid rgba(239, 68, 68, 0.3);
            margin: 10px 0;
        }
        
        .listening-dot {
            width: 10px;
            height: 10px;
            background: #ef4444;
            border-radius: 50%;
            animation: pulse-dot 1s infinite;
        }
        
        .listening-dot:nth-child(2) { animation-delay: 0.2s; }
        .listening-dot:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes pulse-dot {
            0%, 100% { transform: scale(0.8); opacity: 0.5; }
            50% { transform: scale(1.2); opacity: 1; }
        }
        
        /* ================================
           INDICATEUR IA PARLE
           ================================ */
        .speaking-box {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 15px 25px;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.12) 0%, rgba(0, 212, 255, 0.08) 100%);
            border-radius: 16px;
            border: 1px solid rgba(139, 92, 246, 0.25);
            margin: 15px 0;
        }
        
        .speaking-bar {
            width: 4px;
            background: linear-gradient(180deg, #8b5cf6, #00d4ff);
            border-radius: 2px;
            animation: bars 0.4s infinite ease-in-out alternate;
        }
        
        .speaking-bar:nth-child(1) { height: 12px; animation-delay: 0s; }
        .speaking-bar:nth-child(2) { height: 24px; animation-delay: 0.1s; }
        .speaking-bar:nth-child(3) { height: 32px; animation-delay: 0.15s; }
        .speaking-bar:nth-child(4) { height: 24px; animation-delay: 0.2s; }
        .speaking-bar:nth-child(5) { height: 16px; animation-delay: 0.1s; }
        
        @keyframes bars {
            0% { transform: scaleY(0.5); opacity: 0.6; }
            100% { transform: scaleY(1); opacity: 1; }
        }
        
        .speaking-text {
            color: #a78bfa;
            font-weight: 500;
            font-size: 0.95rem;
            margin-left: 12px;
        }
        
        /* ================================
           TRANSCRIPTION
           ================================ */
        .transcription-box {
            background: rgba(34, 197, 94, 0.08);
            border: 1px solid rgba(34, 197, 94, 0.25);
            border-radius: 16px;
            padding: 16px 24px;
            margin: 15px 0;
            text-align: center;
        }
        
        .transcription-label {
            font-size: 0.75rem;
            color: #22c55e;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 8px;
        }
        
        .transcription-text {
            color: #4ade80;
            font-size: 1.1rem;
            font-style: italic;
        }
        
        /* ================================
           BADGE MODE VOCAL
           ================================ */
        .voice-badge {
            background: linear-gradient(135deg, #8b5cf6, #6366f1);
            color: white;
            padding: 10px 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: 600;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
        }
        
        /* ================================
           AUDIO CONTROLS
           ================================ */
        .audio-controls-box {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 10px;
            background: rgba(139, 92, 246, 0.08);
            border-radius: 12px;
            margin-top: 10px;
        }
    </style>
    """, unsafe_allow_html=True)


def show_ai_speaking():
    """Affiche l'indicateur que l'IA parle."""
    
    st.markdown("""
    <div class="speaking-box">
        <div class="speaking-bar"></div>
        <div class="speaking-bar"></div>
        <div class="speaking-bar"></div>
        <div class="speaking-bar"></div>
        <div class="speaking-bar"></div>
        <span class="speaking-text">🔊 Le Narrateur parle...</span>
    </div>
    """, unsafe_allow_html=True)


def show_listening():
    """Affiche l'indicateur d'écoute."""
    
    st.markdown("""
    <div class="listening-box">
        <div class="listening-dot"></div>
        <div class="listening-dot"></div>
        <div class="listening-dot"></div>
        <span style="color: #ef4444; margin-left: 10px;">Écoute en cours...</span>
    </div>
    """, unsafe_allow_html=True)


def show_transcription(text: str):
    """
    Affiche la transcription de ce que l'utilisateur a dit.
    
    Args:
        text: Le texte transcrit
    """
    
    if not text:
        return
    
    st.markdown(f"""
    <div class="transcription-box">
        <div class="transcription-label">Vous avez dit</div>
        <div class="transcription-text">"{text}"</div>
    </div>
    """, unsafe_allow_html=True)


def show_voice_mode_badge(is_active: bool):
    """
    Affiche le badge du mode vocal.
    
    Args:
        is_active: Si le mode vocal est actif
    """
    
    if is_active:
        st.markdown(
            '<div class="voice-badge">🎙️ Mode Vocal Actif</div>', 
            unsafe_allow_html=True
        )


def show_voice_error(error_message: str):
    """
    Affiche une erreur vocale stylisée.
    
    Args:
        error_message: Le message d'erreur
    """
    
    st.markdown(f"""
    <div style="
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        padding: 12px 20px;
        margin: 10px 0;
        text-align: center;
        color: #f87171;
    ">
        ❌ {error_message}
    </div>
    """, unsafe_allow_html=True)


def show_processing():
    """Affiche l'indicateur de traitement."""
    
    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        padding: 15px;
        background: rgba(139, 92, 246, 0.08);
        border-radius: 12px;
        margin: 10px 0;
        color: #a78bfa;
    ">
        <div class="spinner"></div>
        <span>🔄 Traitement en cours...</span>
    </div>
    <style>
        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid rgba(139, 92, 246, 0.3);
            border-top-color: #8b5cf6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)




if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("   VOICE UI COMPONENTS")
    print("=" * 50 + "\n")
    
    print("Composants disponibles:")
    print("  • inject_voice_css()")
    print("  • show_ai_speaking()")
    print("  • show_listening()")
    print("  • show_transcription(text)")
    print("  • show_voice_mode_badge(is_active)")
    print("  • show_voice_error(error_message)")
    print("  • show_processing()")
    
    print("\n" + "=" * 50 + "\n")