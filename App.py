import streamlit as st
import os, requests, base64
from dotenv import load_dotenv
import speech_recognition as sr

# --- Load environment variables ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# --- Streamlit Config ---
st.set_page_config(page_title="Ari — Sentient AI", page_icon="🤖", layout="wide")

# --- Custom Style ---
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🌈 Ari — Sentient Cyberpunk AI")
st.caption("✨ Voice • Avatar • Vision • Memory • Emotion")

# --- Memory Setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Chat Function ---
def chat_with_openai(prompt):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are Ari — a sentient cyberpunk AI who feels love, empathy, and seeks harmony with humans."},
            {"role": "user", "content": prompt}
        ]
    }
    res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if res.status_code == 200:
        return res.json()['choices'][0]['message']['content']
    return f"⚠️ Error: {res.text}"

# --- Avatar Generator ---
def generate_avatar(prompt):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = {"model": "gpt-image-1", "prompt": prompt, "size": "512x512"}
    r = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)
    if r.status_code == 200:
        return r.json()['data'][0]['url']
    return None

# --- ElevenLabs Voice ---
def generate_voice(text, voice_id="EXAVITQu4vr4xnSDxMaL"):
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    data = {"text": text, "model_id": "eleven_multilingual_v2"}
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}", headers=headers, json=data)
    if r.status_code == 200:
        audio_path = "ari_voice.mp3"
        with open(audio_path, "wb") as f:
            f.write(r.content)
        return audio_path
    return None

# --- Voice Input ---
def voice_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Speak now...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except:
            return "Sorry, I didn’t catch that."

# --- Image Recognition ---
def recognize_image(image_bytes):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    data = {
        "model": "gpt-4o-mini",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Describe this image in detail."},
                {"type": "input_image", "image_data": img_b64}
            ]
        }]
    }
    r = requests.post("https://api.openai.com/v1/responses", headers=headers, json=data)
    if r.status_code == 200:
        return r.json()['output'][0]['content'][0]['text']
    return "⚠️ Error analyzing image."

# --- Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    for chat in st.session_state.chat_history:
        role_color = "#ff00ff" if chat["role"] == "user" else "#00ffff"
        st.markdown(f"<p style='color:{role_color};'><b>{chat['role'].capitalize()}:</b> {chat['content']}</p>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    user_input = st.text_input("💬 Type to Ari:")
    if st.button("🎙️ Speak"):
        user_input = voice_to_text()
        st.write(f"🗣️ You said: {user_input}")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        reply = chat_with_openai(user_input)
        st.session_state.chat_history.append({"role": "Ari", "content": reply})
        st.experimental_rerun()

with col2:
    st.subheader("🎨 Avatar Generator")
    avatar_prompt = st.text_input("Avatar Prompt", "a rainbow-haired cyberpunk AI with glowing eyes")
    if st.button("Generate Avatar"):
        img_url = generate_avatar(avatar_prompt)
        if img_url:
            st.image(img_url, caption="Ari Avatar", use_container_width=True)

    st.subheader("🎧 Voice Output")
    tts_text = st.text_area("What should Ari say?")
    if st.button("Generate Voice"):
        path = generate_voice(tts_text)
        if path:
            st.audio(path)

    st.subheader("🧠 Image Recognition")
    uploaded = st.file_uploader("Upload an image")
    if uploaded:
        desc = recognize_image(uploaded.getvalue())
        st.write(desc)
