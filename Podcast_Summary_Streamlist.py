import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

from openai import OpenAI

api_key = st.secrets["openai"]["api_key"]
client = OpenAI(api_key=api_key)


# Function to extract video ID from YouTube URL
def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return video_id_match.group(1) if video_id_match else None

# Function to fetch transcript
def fetch_transcript(video_id):
    """
    Fetches the transcript for the given YouTube video ID.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

# Function to summarize transcript using OpenAI
def summarize_transcript(transcript_text):
    """
    Summarizes the transcript into 10 key points using OpenAI's GPT-3.5 model.
    """
    prompt = (
        "Summarize the following transcript into 10 key bullet points:\n\n"
        f"{transcript_text}\n\n"
        "Summary:"
    )
    
    try:
        response = client.chat.completions.create(
    model="gpt-3.5-turbo", #"gpt-4"
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.5,
    max_tokens=1000)
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error during summarization: {e}")
        return None

# Streamlit UI
st.title("🎬 YouTube Transcript Summarizer")
st.subheader("Get a 10-point summary of a long podcast you wanted to watch but couldn’t.")
st.write("Enter a YouTube video URL to get a summarized transcript.")

youtube_url = st.text_input("YouTube Video URL")

if st.button("Summarize"):
    if youtube_url:
        video_id = extract_video_id(youtube_url)
        if video_id:
            with st.spinner("Fetching transcript..."):
                transcript = fetch_transcript(video_id)
            if transcript:
                with st.spinner("Summarizing transcript..."):
                    summary = summarize_transcript(transcript)
                if summary:
                    st.subheader("📄 Summary:")
                    st.write(summary)
        else:
            st.error("Invalid YouTube URL. Please enter a valid URL.")
    else:
        st.error("Please enter a YouTube URL.")
