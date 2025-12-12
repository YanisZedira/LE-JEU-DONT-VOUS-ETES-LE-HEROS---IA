
"""
Composants audio custom pour Streamlit (version corrigée)
- Enregistreur audio avec st.markdown + JavaScript
- Lecteur audio avec autoplay
- Compatible toutes versions Streamlit
"""

import streamlit as st
import base64
import uuid
from typing import Optional


def get_audio_recorder_html() -> str:
    """
    Retourne le HTML/JS pour l'enregistreur audio.
    Utilise postMessage pour communiquer avec Streamlit.
    """
    
    unique_id = str(uuid.uuid4())[:8]
    
    return f'''
    <div id="recorder-container-{unique_id}" style="
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 15px;
        padding: 20px;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(0, 212, 255, 0.05));
        border-radius: 16px;
        border: 1px solid rgba(139, 92, 246, 0.2);
    ">
        <style>
            .hero-record-btn {{
                width: 100%;
                max-width: 280px;
                padding: 18px 32px;
                font-size: 1.15rem;
                font-weight: 600;
                border-radius: 16px;
                border: 2px solid rgba(139, 92, 246, 0.5);
                background: linear-gradient(135deg, #1a1a2e 0%, #16161f 100%);
                color: #e0e0ff;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
            }}
            
            .hero-record-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 8px 30px rgba(139, 92, 246, 0.5);
                border-color: rgba(139, 92, 246, 0.8);
            }}
            
            .hero-record-btn.recording {{
                animation: hero-pulse 1s infinite alternate;
                border-color: #ff2b70;
                color: #ff2b70;
                background: linear-gradient(135deg, #2a1a2e 0%, #1f1620 100%);
            }}
            
            @keyframes hero-pulse {{
                0% {{ box-shadow: 0 0 10px rgba(255, 43, 112, 0.4); }}
                100% {{ box-shadow: 0 0 30px rgba(255, 43, 112, 0.8); }}
            }}
            
            .hero-timer {{
                font-size: 2rem;
                font-weight: 700;
                color: #ff2b70;
                font-family: 'Courier New', monospace;
                text-shadow: 0 0 10px rgba(255, 43, 112, 0.5);
            }}
            
            .hero-status {{
                font-size: 0.95rem;
                color: #a0a0cc;
            }}
            
            .hero-status.recording {{
                color: #ff2b70;
                animation: hero-blink 1s infinite;
            }}
            
            @keyframes hero-blink {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
        </style>
        
        <button id="heroRecordBtn-{unique_id}" class="hero-record-btn" onclick="heroToggleRecording_{unique_id}()">
            <span id="heroMicIcon-{unique_id}" style="font-size: 1.4rem;">🎤</span>
            <span id="heroBtnText-{unique_id}">Appuyer pour parler</span>
        </button>
        
        <div id="heroTimer-{unique_id}" class="hero-timer" style="display: none;">00:00</div>
        
        <div id="heroStatus-{unique_id}" class="hero-status">🎯 Prêt à enregistrer</div>
        
        <input type="hidden" id="heroAudioData-{unique_id}" />
    </div>
    
    <script>
    (function() {{
        let mediaRecorder_{unique_id} = null;
        let audioChunks_{unique_id} = [];
        let isRecording_{unique_id} = false;
        let timerInterval_{unique_id} = null;
        let seconds_{unique_id} = 0;
        
        const btn = document.getElementById('heroRecordBtn-{unique_id}');
        const btnText = document.getElementById('heroBtnText-{unique_id}');
        const micIcon = document.getElementById('heroMicIcon-{unique_id}');
        const status = document.getElementById('heroStatus-{unique_id}');
        const timer = document.getElementById('heroTimer-{unique_id}');
        const audioDataInput = document.getElementById('heroAudioData-{unique_id}');
        
        window.heroToggleRecording_{unique_id} = async function() {{
            if (!isRecording_{unique_id}) {{
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{ 
                        audio: {{
                            echoCancellation: true,
                            noiseSuppression: true,
                            sampleRate: 44100
                        }}
                    }});
                    
                    audioChunks_{unique_id} = [];
                    mediaRecorder_{unique_id} = new MediaRecorder(stream, {{
                        mimeType: 'audio/webm;codecs=opus'
                    }});
                    
                    mediaRecorder_{unique_id}.ondataavailable = (e) => {{
                        if (e.data.size > 0) {{
                            audioChunks_{unique_id}.push(e.data);
                        }}
                    }};
                    
                    mediaRecorder_{unique_id}.onstop = async () => {{
                        status.textContent = "⏳ Envoi en cours...";
                        status.className = "hero-status";
                        
                        const audioBlob = new Blob(audioChunks_{unique_id}, {{ type: 'audio/webm' }});
                        const reader = new FileReader();
                        
                        reader.onloadend = () => {{
                            const base64 = reader.result.split(',')[1];
                            audioDataInput.value = base64;
                            
                            // Déclenche un event pour Streamlit
                            const event = new CustomEvent('audioRecorded', {{ 
                                detail: {{ audio: base64 }} 
                            }});
                            window.dispatchEvent(event);
                            
                            // Aussi stocker dans sessionStorage pour Streamlit
                            sessionStorage.setItem('heroRecordedAudio', base64);
                            
                            status.textContent = "✅ Audio capturé ! Cliquez sur 'Envoyer'";
                        }};
                        
                        reader.readAsDataURL(audioBlob);
                        stream.getTracks().forEach(track => track.stop());
                    }};
                    
                    mediaRecorder_{unique_id}.start();
                    isRecording_{unique_id} = true;
                    
                    btn.classList.add('recording');
                    btnText.textContent = "⏹️ Arrêter";
                    status.textContent = "🔴 Enregistrement...";
                    status.className = "hero-status recording";
                    
                    seconds_{unique_id} = 0;
                    timer.style.display = "block";
                    timerInterval_{unique_id} = setInterval(() => {{
                        seconds_{unique_id}++;
                        const m = Math.floor(seconds_{unique_id} / 60).toString().padStart(2, '0');
                        const s = (seconds_{unique_id} % 60).toString().padStart(2, '0');
                        timer.textContent = m + ':' + s;
                    }}, 1000);
                    
                    // Auto-stop après 25 secondes
                    setTimeout(() => {{
                        if (isRecording_{unique_id}) {{
                            heroToggleRecording_{unique_id}();
                        }}
                    }}, 25000);
                    
                }} catch (err) {{
                    console.error("Erreur micro:", err);
                    status.textContent = "❌ Accès micro refusé";
                }}
            }} else {{
                if (mediaRecorder_{unique_id} && mediaRecorder_{unique_id}.state !== 'inactive') {{
                    mediaRecorder_{unique_id}.stop();
                }}
                isRecording_{unique_id} = false;
                
                btn.classList.remove('recording');
                btnText.textContent = "🎤 Appuyer pour parler";
                
                clearInterval(timerInterval_{unique_id});
                timer.style.display = "none";
            }}
        }};
    }})();
    </script>
    '''


def render_audio_recorder() -> None:
    """
    Affiche l'enregistreur audio.
    L'audio enregistré sera stocké dans sessionStorage.
    """
    st.markdown(get_audio_recorder_html(), unsafe_allow_html=True)


def get_audio_player_html(audio_base64: str, autoplay: bool = True) -> str:
    """
    Retourne le HTML pour un lecteur audio avec animation.
    
    Args:
        audio_base64: Audio encodé en base64
        autoplay: Lecture automatique
    """
    
    autoplay_attr = "autoplay" if autoplay else ""
    unique_id = str(uuid.uuid4())[:8]
    
    return f'''
    <div id="player-container-{unique_id}" style="
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        padding: 20px;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(0, 212, 255, 0.05));
        border-radius: 16px;
        border: 1px solid rgba(139, 92, 246, 0.15);
        margin: 15px 0;
    ">
        <style>
            .hero-voice-anim {{
                display: flex;
                justify-content: center;
                align-items: flex-end;
                gap: 5px;
                height: 45px;
            }}
            
            .hero-voice-bar {{
                width: 5px;
                background: linear-gradient(180deg, #8b5cf6, #00d4ff);
                border-radius: 3px;
                animation: heroVoiceBars 0.35s infinite ease-in-out alternate;
                box-shadow: 0 0 8px rgba(139, 92, 246, 0.6);
            }}
            
            .hero-voice-bar:nth-child(1) {{ animation-delay: 0s; height: 15px; }}
            .hero-voice-bar:nth-child(2) {{ animation-delay: 0.07s; height: 25px; }}
            .hero-voice-bar:nth-child(3) {{ animation-delay: 0.14s; height: 35px; }}
            .hero-voice-bar:nth-child(4) {{ animation-delay: 0.21s; height: 25px; }}
            .hero-voice-bar:nth-child(5) {{ animation-delay: 0.1s; height: 30px; }}
            .hero-voice-bar:nth-child(6) {{ animation-delay: 0.17s; height: 20px; }}
            .hero-voice-bar:nth-child(7) {{ animation-delay: 0.05s; height: 28px; }}
            
            @keyframes heroVoiceBars {{
                0% {{ transform: scaleY(0.3); opacity: 0.5; }}
                100% {{ transform: scaleY(1); opacity: 1; }}
            }}
            
            .hero-voice-status {{
                font-size: 0.95rem;
                color: #00d4ff;
                font-weight: 500;
            }}
            
            .hero-audio-controls {{
                display: flex;
                gap: 10px;
                margin-top: 10px;
            }}
            
            .hero-replay-btn {{
                padding: 10px 20px;
                border-radius: 10px;
                border: 1px solid rgba(139, 92, 246, 0.4);
                background: rgba(139, 92, 246, 0.1);
                color: #a0a0cc;
                cursor: pointer;
                font-size: 0.9rem;
                transition: all 0.3s ease;
            }}
            
            .hero-replay-btn:hover {{
                background: rgba(139, 92, 246, 0.2);
                border-color: rgba(139, 92, 246, 0.6);
                color: #e0e0ff;
            }}
        </style>
        
        <div id="heroVoiceAnim-{unique_id}" class="hero-voice-anim">
            <div class="hero-voice-bar"></div>
            <div class="hero-voice-bar"></div>
            <div class="hero-voice-bar"></div>
            <div class="hero-voice-bar"></div>
            <div class="hero-voice-bar"></div>
            <div class="hero-voice-bar"></div>
            <div class="hero-voice-bar"></div>
        </div>
        
        <div id="heroVoiceStatus-{unique_id}" class="hero-voice-status">
            🔊 Le Narrateur parle...
        </div>
        
        <audio id="heroAudioPlayer-{unique_id}" {autoplay_attr} style="display: none;">
            <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">
        </audio>
        
        <div class="hero-audio-controls" id="heroControls-{unique_id}" style="display: none;">
            <button class="hero-replay-btn" onclick="document.getElementById('heroAudioPlayer-{unique_id}').currentTime=0; document.getElementById('heroAudioPlayer-{unique_id}').play();">
                🔄 Réécouter
            </button>
        </div>
    </div>
    
    <script>
    (function() {{
        const audio = document.getElementById('heroAudioPlayer-{unique_id}');
        const anim = document.getElementById('heroVoiceAnim-{unique_id}');
        const status = document.getElementById('heroVoiceStatus-{unique_id}');
        const controls = document.getElementById('heroControls-{unique_id}');
        
        if (audio) {{
            audio.addEventListener('play', () => {{
                anim.style.display = 'flex';
                status.textContent = '🔊 Le Narrateur parle...';
                controls.style.display = 'none';
            }});
            
            audio.addEventListener('ended', () => {{
                anim.style.display = 'none';
                status.textContent = '✅ Narration terminée';
                controls.style.display = 'flex';
            }});
            
            audio.addEventListener('pause', () => {{
                anim.style.display = 'none';
            }});
            
            audio.addEventListener('error', (e) => {{
                console.error('Erreur audio:', e);
                status.textContent = '❌ Erreur de lecture';
                anim.style.display = 'none';
            }});
        }}
    }})();
    </script>
    '''


def render_audio_player(audio_base64: str, autoplay: bool = True) -> None:
    """
    Affiche le lecteur audio avec animation.
    
    Args:
        audio_base64: Audio encodé en base64
        autoplay: Lecture automatique
    """
    st.markdown(get_audio_player_html(audio_base64, autoplay), unsafe_allow_html=True)


def render_simple_audio_autoplay(audio_base64: str) -> None:
    """
    Joue l'audio automatiquement (lecteur invisible).
    
    Args:
        audio_base64: Audio encodé en base64
    """
    html = f'''
    <audio autoplay style="display:none;">
        <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">
    </audio>
    '''
    st.markdown(html, unsafe_allow_html=True)


def render_voice_indicator(is_speaking: bool = True) -> None:
    """
    Affiche un indicateur que l'IA parle.
    """
    if not is_speaking:
        return
    
    html = '''
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        padding: 15px;
        background: rgba(139, 92, 246, 0.1);
        border-radius: 12px;
        margin: 10px 0;
    ">
        <style>
            .speaking-dot {
                width: 8px;
                height: 8px;
                background: #8b5cf6;
                border-radius: 50%;
                animation: speakingPulse 0.6s infinite ease-in-out alternate;
            }
            .speaking-dot:nth-child(1) { animation-delay: 0s; }
            .speaking-dot:nth-child(2) { animation-delay: 0.15s; }
            .speaking-dot:nth-child(3) { animation-delay: 0.3s; }
            
            @keyframes speakingPulse {
                0% { transform: scale(0.8); opacity: 0.5; }
                100% { transform: scale(1.2); opacity: 1; }
            }
        </style>
        
        <div class="speaking-dot"></div>
        <div class="speaking-dot"></div>
        <div class="speaking-dot"></div>
        <span style="margin-left: 10px; color: #a0a0cc;">Le Narrateur parle...</span>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)