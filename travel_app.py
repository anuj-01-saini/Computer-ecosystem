import streamlit as st
import requests
import uuid
import os

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
st.set_page_config(page_title="3D AI Travel Guide", page_icon="🌍", layout="wide")


# --- 3D BACKGROUND ENGINE ---
st.markdown("""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
    /* Fixed background canvas */
    #three-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        background: radial-gradient(circle at center, #001a1a 0%, #000000 100%);
    }

    /* Make Streamlit background transparent to see the 3D */
    .stApp {
        background: transparent;
    }

    /* Glassmorphism for the UI Containers */
    div[data-testid="column"] {
        background: rgba(0, 30, 40, 0.3) !important;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(100, 255, 218, 0.2);
        border-radius: 12px;
        padding: 20px;
        color: white;
    }

    h1, h3 {
        color: #64ffda !important;
        font-family: 'Courier New', monospace;
    }
    
    header, footer { visibility: hidden; }
    </style>

    <canvas id="three-canvas"></canvas>

    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({
            canvas: document.querySelector('#three-canvas'),
            antialias: true,
            alpha: true 
        });

        renderer.setSize(window.innerWidth, window.innerHeight);
        camera.position.z = 35;

        // 1. The Outer Wireframe Globe (The Grid)
        const globeGeom = new THREE.SphereGeometry(20, 35, 35);
        const globeMat = new THREE.MeshBasicMaterial({
            color: 0x64ffda,
            wireframe: true,
            transparent: true,
            opacity: 0.1
        });
        const globe = new THREE.Mesh(globeGeom, globeMat);
        scene.add(globe);

        // 2. The Core Icosahedron (The Rotating Centerpiece)
        const coreGeom = new THREE.IcosahedronGeometry(8, 0);
        const coreMat = new THREE.MeshBasicMaterial({ 
            color: 0x64ffda, 
            wireframe: true,
            transparent: true,
            opacity: 0.7
        });
        const core = new THREE.Mesh(coreGeom, coreMat);
        scene.add(core);

        // Animation Loop
        function animate() {
            requestAnimationFrame(animate);
            
            // Subtle rotation for the outer grid
            globe.rotation.y += 0.001;
            
            // Faster, complex rotation for the core (matches your video)
            core.rotation.y += 0.006;
            core.rotation.x += 0.003;

            renderer.render(scene, camera);
        }

        // Handle Window Resize
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        animate();
    </script>
""", unsafe_allow_html=True)

st.title("🌍 SMART TRAVEL GUIDE")
st.write("---")

col1, col2, col3 = st.columns(3, gap="large")

# --- 1. VISION SCAN ---
with col1:
    st.markdown('<div class="stHeader"><h3>📸 VISION SCAN</h3></div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Landmark Photo", type=['jpg', 'jpeg', 'png'], key="vision")
    
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)
        if st.button("IDENTIFY"):
            with st.spinner("Satellite Scan..."):
                headers = {'Ocp-Apim-Subscription-Key': VISION_KEY, 'Content-Type': 'application/octet-stream'}
                api_url = f"{VISION_ENDPOINT}vision/v3.2/analyze?visualFeatures=Description"
                response = requests.post(api_url, headers=headers, data=uploaded_file.getvalue())
                try:
                    desc = response.json()['description']['captions'][0]['text']
                    st.success(f"**RESULT:** {desc.upper()}")
                except: st.error("Scan failed.")

# --- 2. GLOBAL TRANSLATOR ---
with col2:
    st.markdown('<div class="stHeader"><h3>🌐 TRANSLATION</h3></div>', unsafe_allow_html=True)
    text_to_translate = st.text_area("Input Foreign Text", height=100)
    lang_options = {"English 🇬🇧": "en", "Hindi 🇮🇳": "hi", "French 🇫🇷": "fr", "Spanish 🇪🇸": "es", "German 🇩🇪": "de"}
    selected_lang = st.selectbox("Select Target", list(lang_options.keys()))
    
    if st.button("TRANSLATE"):
        if text_to_translate:
            with st.spinner("Decoding..."):
                headers = {'Ocp-Apim-Subscription-Key': TRANSLATOR_KEY, 'Ocp-Apim-Subscription-Region': TRANSLATOR_REGION, 'Content-type': 'application/json', 'X-ClientTraceId': str(uuid.uuid4())}
                url = f"{TRANSLATOR_ENDPOINT}/translate?api-version=3.0&to={lang_options[selected_lang]}"
                response = requests.post(url, headers=headers, json=[{'text': text_to_translate}])
                res_text = response.json()[0]['translations'][0]['text']
                st.info(f"**RESULT:** {res_text}")

# --- 3. MOOD ANALYSIS ---
with col3:
    st.markdown('<div class="stHeader"><h3>📊 SENTIMENT ANALYSIS</h3></div>', unsafe_allow_html=True)
    review_text = st.text_area("Paste Review", height=100)
    
    if st.button("CHECK SENTIMENT"):
        if review_text:
            with st.spinner("Analyzing Feedback..."):
                headers = {"Ocp-Apim-Subscription-Key": LANGUAGE_KEY, "Content-Type": "application/json"}
                payload = {"kind": "SentimentAnalysis", "analysisInput": {"documents": [{"id": "1", "language": "en", "text": review_text}]}}
                api_url = f"{LANGUAGE_ENDPOINT}language/:analyze-text?api-version=2022-05-01"
                response = requests.post(api_url, headers=headers, json=payload)
                sentiment = response.json()['results']['documents'][0]['sentiment']
                
                if sentiment == "positive": st.success(f"**MOOD:** {sentiment.upper()} 😊")
                elif sentiment == "neutral": st.warning(f"**MOOD:** {sentiment.upper()} 😐")
                else: st.error(f"**MOOD:** {sentiment.upper()} ☹️")

st.markdown("---")
st.caption("Developed for B.Tech CS Practical | AI Cloud Hub v2.0")
