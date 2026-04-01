import streamlit as st
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# --- AZURE CONFIGURATION ---
ENDPOINT = "https://analysier10.cognitiveservices.azure.com/"
KEY = "your key"

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Customer Review Insights", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTextArea textarea { background-color: #1e2130; color: white; }
    .sentiment-pos { color: #00ff00; font-weight: bold; }
    .sentiment-neg { color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Customer Review AI Insights")
st.write("Perform Sentiment Analysis and Key Phrase Extraction using Azure AI Language.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Project Details")
    st.write("**Developer:** Anuj Saini")
    st.write("**Service:** Azure Text Analytics")
    st.success("Connected to Azure ✅")

# --- INPUT SECTION ---
user_review = st.text_area("Enter a customer review to analyze:", 
                          placeholder="e.g., The battery life on this MacBook M2 is incredible, but the charger is a bit bulky.")

if st.button("Analyze Review"):
    if user_review:
        try:
            # 1. Initialize Client
            client = TextAnalyticsClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))

            # 2. Perform Sentiment Analysis
            sentiment_result = client.analyze_sentiment([user_review])[0]
            
            # 3. Perform Key Phrase Extraction
            phrase_result = client.extract_key_phrases([user_review])[0]

            # --- DISPLAY RESULTS ---
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Sentiment Result")
                sentiment = sentiment_result.sentiment.capitalize()
                
                # Dynamic UI coloring
                if sentiment == "Positive":
                    st.success(f"### Overall Sentiment: {sentiment}")
                elif sentiment == "Negative":
                    st.error(f"### Overall Sentiment: {sentiment}")
                else:
                    st.warning(f"### Overall Sentiment: {sentiment}")

                # Show Confidence Scores
                st.write("**Confidence Scores:**")
                st.write(f"😊 Positive: {sentiment_result.confidence_scores.positive:.2%}")
                st.write(f"😐 Neutral: {sentiment_result.confidence_scores.neutral:.2%}")
                st.write(f"☹️ Negative: {sentiment_result.confidence_scores.negative:.2%}")

            with col2:
                st.subheader("Key Phrases Extracted")
                if not phrase_result.is_error:
                    # Display phrases as tags
                    phrases = phrase_result.key_phrases
                    if phrases:
                        st.write("Azure identified these main topics:")
                        cols = st.columns(3)
                        for i, phrase in enumerate(phrases):
                            cols[i % 3].button(phrase, key=f"phrase_{i}")
                    else:
                        st.info("No specific key phrases found.")
                else:
                    st.error("Could not extract phrases.")

            # Detailed Sentence Analysis
            with st.expander("See Sentence-by-Sentence Breakdown"):
                for idx, sentence in enumerate(sentiment_result.sentences):
                    st.write(f"**Sentence {idx+1}:** {sentence.text}")
                    st.write(f"Sentiment: {sentence.sentiment}")
                    st.progress(sentence.confidence_scores.positive if sentence.sentiment == 'positive' else sentence.confidence_scores.negative)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter some text first!")

# --- FOOTER ---
st.divider()
st.caption("Tip: Try a mixed review like 'The food was great but the service was slow' to see sentence-level analysis.")