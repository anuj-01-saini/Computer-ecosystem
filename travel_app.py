import streamlit as st
import requests, uuid
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# ================= CONFIGURATION =================
# 1. Computer Vision
VISION_KEY = "your key"
VISION_ENDPOINT = "https://photoguider.cognitiveservices.azure.com/"

# 2. Translator
TRANSLATOR_KEY = "your key"
TRANSLATOR_REGION = "southeastasia"
TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"

# 3. Sentiment Analysis (Language Service)
LANGUAGE_KEY = "your key"
LANGUAGE_ENDPOINT = "https://languageguider01.cognitiveservices.azure.com/"
# =================================================

# --- Backend Logic Functions ---

def analyze_image(image_data):
    client = ImageAnalysisClient(endpoint=VISION_ENDPOINT, credential=AzureKeyCredential(VISION_KEY))
    result = client.analyze(image_data=image_data, visual_features=[VisualFeatures.CAPTION, VisualFeatures.TAGS])
    return result.caption.text if result.caption else "No description available."

def translate_description(text, target_lang):
    path = '/translate'
    url = TRANSLATOR_ENDPOINT + path
    params = {'api-version': '3.0', 'from': 'en', 'to': [target_lang]}
    headers = {
        'Ocp-Apim-Subscription-Key': TRANSLATOR_KEY,
        'Ocp-Apim-Subscription-Region': TRANSLATOR_REGION,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    body = [{'text': text}]
    response = requests.post(url, params=params, headers=headers, json=body).json()
    return response[0]['translations'][0]['text']

def analyze_sentiment(review_text):
    client = TextAnalyticsClient(endpoint=LANGUAGE_ENDPOINT, credential=AzureKeyCredential(LANGUAGE_KEY))
    response = client.analyze_sentiment(documents=[review_text])[0]
    return response.sentiment

# --- UI/UX Logic ---

st.set_page_config(page_title="Smart Travel Guide", layout="wide")
st.title("🌍 Smart Travel Guide AI")
st.write("Identify landmarks, translate guides, and analyze travel vibes.")

tab1, tab2 = st.tabs(["📸 Landmark Explorer", "💬 Review Analyzer"])

with tab1:
    st.header("Landmark Recognition")
    uploaded_file = st.file_uploader("Upload a travel photo...", type=["jpg", "png", "jpeg"])
    target_language = st.selectbox("Translate guide to:", ["Hindi", "Spanish", "French", "German"], index=0)
    lang_map = {"Hindi": "hi", "Spanish": "es", "French": "fr", "German": "de"}

    if uploaded_file:
        st.image(uploaded_file, width=400)
        if st.button("Explore Landmark"):
            with st.spinner("AI is analyzing..."):
                # 1. Vision
                description = analyze_image(uploaded_file.getvalue())
                # 2. Translation
                translated = translate_description(description, lang_map[target_language])
                
                st.success(f"**English:** {description}")
                st.info(f"**{target_language}:** {translated}")

with tab2:
    st.header("Travel Review Sentiment")
    review = st.text_area("Paste a travel review here (e.g., 'The hotel was amazing!'):")
    if st.button("Analyze Vibe"):
        if review:
            sentiment = analyze_sentiment(review)
            if sentiment == "positive":
                st.success(f"This is a **{sentiment.upper()}** review! 😍")
            elif sentiment == "negative":
                st.error(f"This is a **{sentiment.upper()}** review. 😞")
            else:
                st.warning(f"This is a **{sentiment.upper()}** review. 😐")