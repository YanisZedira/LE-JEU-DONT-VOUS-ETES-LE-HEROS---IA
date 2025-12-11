# ============================================
# HERO IA - Composants UI Vocaux
# ============================================

import streamlit as st


def inject_voice_css():
    st.markdown("""
    <style>
        .mic-zone {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%);
            border: 2px dashed rgba(139, 92, 246, 0.3);
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
            text-align: center;
        }
        
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
    </style>
    """, unsafe_allow_html=True)


def show_ai_speaking():
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


def show_transcription(text: str):
    st.markdown(f"""
    <div class="transcription-box">
        <div class="transcription-label">Vous avez dit</div>
        <div class="transcription-text">"{text}"</div>
    </div>
    """, unsafe_allow_html=True)


def show_voice_mode_badge(is_active: bool):
    if is_active:
        st.markdown('<div class="voice-badge">🎙️ Mode Vocal Actif</div>', unsafe_allow_html=True)