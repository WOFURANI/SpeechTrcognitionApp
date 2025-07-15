import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import numpy as np
import av
import speech_recognition as sr
from pydub import AudioSegment
import io

# Session state for audio buffer
if "audio_frames" not in st.session_state:
    st.session_state.audio_frames = []

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

class AudioProcessor(AudioProcessorBase):
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray()
        # Append raw audio frame to session state
        st.session_state.audio_frames.append(pcm)
        return frame

def frames_to_wav(frames, sample_rate=48000, channels=1):
    """Convert numpy PCM frames to WAV bytes using pydub."""
    if not frames:
        return None

    audio_data = np.concatenate(frames).astype(np.int16).tobytes()
    audio_segment = AudioSegment(
        data=audio_data,
        sample_width=2,
        frame_rate=sample_rate,
        channels=channels
    )
    wav_bytes_io = io.BytesIO()
    audio_segment.export(wav_bytes_io, format="wav")
    wav_bytes_io.seek(0)
    return wav_bytes_io

def transcribe_wav(wav_bytes, language):
    r = sr.Recognizer()
    with sr.AudioFile(wav_bytes) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio, language=language)
        return text
    except sr.UnknownValueError:
        st.error("Speech was unclear. Could not transcribe.")
    except sr.RequestError as e:
        st.error(f"Google Speech Recognition request failed: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
    return ""

def save_transcript_to_file(text):
    try:
        with open("transcription.txt", "w", encoding="utf-8") as f:
            f.write(text)
        st.success("Transcript saved to 'transcription.txt'")
    except Exception as e:
        st.error(f"Error saving file: {e}")

def main():
    st.title("🎙️ Speech Recognition with Streamlit WebRTC")

    st.markdown("""
    - **Record live audio in your browser**
    - **Choose language**
    - **Transcribe**
    - **Save transcript**
    """)

    # Language selector
    language = st.selectbox(
        "Choose your speaking language",
        options=[
            ("English (US)", "en-US"),
            ("French (France)", "fr-FR"),
            ("Arabic (Tunisia)", "ar-TN")
        ],
        format_func=lambda x: x[0]
    )[1]
    st.write(f"Selected language: {language}")

    # WebRTC audio streamer
    webrtc_ctx = webrtc_streamer(
        key="speech-recognition",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True
    )

    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Recording Buffer"):
            st.session_state.audio_frames = []
            st.info("Audio buffer cleared.")

    with col2:
        if st.button("Transcribe"):
            if not st.session_state.audio_frames:
                st.warning("No audio data recorded.")
            else:
                wav_bytes = frames_to_wav(st.session_state.audio_frames)
                if wav_bytes:
                    text = transcribe_wav(wav_bytes, language)
                    if text:
                        st.session_state.transcript += text + " "
                else:
                    st.error("Failed to convert audio frames to WAV.")

    # Transcript display
    st.subheader("📝 Current Transcript")
    st.text_area("Transcript", value=st.session_state.transcript, height=200)

    if st.button("Save Transcript to File"):
        if st.session_state.transcript.strip():
            save_transcript_to_file(st.session_state.transcript.strip())
        else:
            st.warning("Transcript is empty. Nothing to save.")

if __name__ == "__main__":
    main()
