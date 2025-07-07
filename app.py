import streamlit as st
import speech_recognition as sr

# App state to hold the transcript
if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "recording" not in st.session_state:
    st.session_state.recording = False

def transcribe_speech(language):
    r = sr.Recognizer()

    with sr.Microphone() as source:
        st.info("Listening... Please speak clearly.")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=20)
            st.success("Audio captured! Transcribing...")

            text = r.recognize_google(audio, language=language)
            return text

        except sr.WaitTimeoutError:
            st.error("No speech detected. Try again.")
        except sr.UnknownValueError:
            st.error("Speech was unclear. Could not transcribe.")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition. Check internet. Error: {e}")
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
    st.title("Speech recognition checkpoint")

    st.markdown("""
    - Choose your **language**
    - Start / Pause / Resume recording
    - Save your transcript to a file
    """)

    # Language selection
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

    # Start recording
    if st.button("Start / Resume Recording"):
        st.session_state.recording = True
        result = transcribe_speech(language)
        if result:
            st.session_state.transcript += result + " "

    # Pause recording
    if st.button("Pause Recording"):
        if st.session_state.recording:
            st.session_state.recording = False
            st.warning("Recording paused.")
        else:
            st.info("Recording is not active.")

    # Display current transcript
    st.subheader("📝 Current Transcript")
    st.text_area("Transcript", value=st.session_state.transcript, height=200)

    # Save to file
    if st.button("Save Transcript to File"):
        if st.session_state.transcript.strip():
            save_transcript_to_file(st.session_state.transcript.strip())
        else:
            st.warning("Transcript is empty. Nothing to save.")

if __name__ == "__main__":
    main()
