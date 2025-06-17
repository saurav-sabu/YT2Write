from crewai import Crew, LLM
from yt2write_agents import YT2WriteAgents
from yt2write_tasks import YT2WriteTasks
import streamlit as st
import datetime
import re
import sys
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)


# Page configuration with custom styling
st.set_page_config(
    page_title="YT2Blog - AI YouTube to Blog Converter",
    page_icon="📺", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 50%, #ff8a80 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 15px 35px rgba(255,107,107,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(255,255,255,0.05) 10px,
            rgba(255,255,255,0.05) 20px
        );
        animation: float 10s infinite linear;
    }
    
    @keyframes float {
        0% { transform: translate(-50%, -50%) rotate(0deg); }
        100% { transform: translate(-50%, -50%) rotate(360deg); }
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* Form container */
    .form-container {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 1px solid #f0f0f0;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e8ecef;
        padding: 1rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        background: #fafbfc;
    }
    
    .stTextInput > div > div > input:focus {
    border-color: #ff6b6b;
    box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1);
    background: black;
    color: white;
}

    .stTextInput > div > div > input:focus::placeholder {
        color: #cccccc; /* Light gray for placeholder text */
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 1rem 2.5rem;
        font-size: 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
        background: linear-gradient(135deg, #ff5252 0%, #ff9800 100%);
    }
    
    /* Status container */
    .status-container {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-left: 5px solid #2196f3;
    }
    
    /* Results container */
    .results-container {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-top: 2rem;
        border: 1px solid #f0f0f0;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #f8f9ff 0%, #e6f3ff 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        transition: all 0.4s ease;
        border: 1px solid #e3f2fd;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        border-color: #ff6b6b;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1.5rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .feature-desc {
        color: #666;
        line-height: 1.7;
        font-size: 1rem;
    }
    
    /* Video preview styling */
    .video-preview {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #ff6b6b;
    }
    
    .video-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .video-id {
        font-family: 'Courier New', monospace;
        background: #e9ecef;
        padding: 0.5rem;
        border-radius: 8px;
        color: #495057;
        font-size: 0.9rem;
    }
    
    /* Credits styling */
    .credits-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-top: 3rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    /* Loading animation */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-spinner {
        animation: spin 2s linear infinite;
        display: inline-block;
        margin-right: 10px;
    }
    
    /* Step indicator */
    .step-indicator {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
    
    .step {
        background: #e9ecef;
        color: #6c757d;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .step.active {
        background: #ff6b6b;
        color: white;
        transform: scale(1.1);
    }
    
    .step.completed {
        background: #28a745;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def create_feature_card(icon, title, description):
    """Create a feature card component"""
    return f"""
    <div class="feature-card">
        <div class="feature-icon">{icon}</div>
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{description}</div>
    </div>
    """


def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    # Handle different YouTube URL formats
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&\n?#]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([^&\n?#]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^&\n?#]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If it's already just a video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    
    return None


class BlogCrew:
    def __init__(self, video_id):
        self.video_id = video_id
        self.output_placeholder = st.empty()
        self.llm = LLM(model="gemini/gemini-2.0-flash")

    def run(self):
        try:
            # Initialize agents and tasks
            agents = YT2WriteAgents()
            tasks = YT2WriteTasks()

            # Create agents
            transcript_agent = agents.transcript_agent()
            summary_agent = agents.summary_agent()
            blog_writer_agent = agents.blog_writer_agent()

            logger.info("Agent assigned")

            # Create tasks
            extract_task = tasks.extract_transcript_text(transcript_agent, self.video_id)
            outline_task = tasks.outline_task(summary_agent)
            blog_task = tasks.write_blog(blog_writer_agent)

            logger.info("Tasks assigned")

            # Create and run crew
            crew = Crew(
                agents=[transcript_agent, summary_agent, blog_writer_agent],
                tasks=[extract_task, outline_task, blog_task],
                verbose=True
            )

            logger.info("Crew executed")

            result = crew.kickoff()
            return result
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None


def main():
    # Header Section
    st.markdown("""
    <div class="main-header">
        <div class="main-title">📺 YT2Blog</div>
        <div class="main-subtitle">Transform YouTube Videos into Engaging Blog Posts with AI</div>
    </div>
    """, unsafe_allow_html=True)

    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Feature cards
        st.markdown("### 🚀 Why Choose YT2Blog?")
        
        st.markdown(create_feature_card(
            "🤖", 
            "AI-Powered Extraction",
            "Advanced AI agents extract, summarize, and convert YouTube content automatically"
        ), unsafe_allow_html=True)
        
        st.markdown(create_feature_card(
            "📝", 
            "SEO-Optimized Content",
            "Generate blog posts optimized for search engines with proper structure and formatting"
        ), unsafe_allow_html=True)
        
        st.markdown(create_feature_card(
            "⚡", 
            "Lightning Fast",
            "Convert hours of video content into comprehensive blog posts in minutes"
        ), unsafe_allow_html=True)
        
        st.markdown(create_feature_card(
            "🎯", 
            "Multiple Formats",
            "Support for various YouTube URL formats and direct video ID input"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown("### 🎬 Convert Your Video")
        
        # Video conversion form
        with st.container():
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            
            with st.form("video_form", clear_on_submit=False):
                # Input field for YouTube URL or Video ID
                st.markdown("#### 🔗 Enter YouTube URL or Video ID")
                video_input = st.text_input(
                    "",
                    placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ or dQw4w9WgXcQ",
                    help="Paste a YouTube URL or enter the video ID directly"
                )
                
                # Show video preview if URL is valid
                if video_input:
                    video_id = extract_video_id(video_input)
                    if video_id:
                        st.markdown(f"""
                        <div class="video-preview">
                            <div class="video-title">✅ Video Detected</div>
                            <div class="video-id">Video ID: {video_id}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Embed video preview
                        st.video(f"https://www.youtube.com/watch?v={video_id}")
                    else:
                        if video_input.strip():
                            st.error("❌ Invalid YouTube URL or Video ID format")
                
                # Submit button
                col_submit1, col_submit2, col_submit3 = st.columns([1, 2, 1])
                with col_submit2:
                    submitted = st.form_submit_button("🚀 Generate Blog Post", use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Processing and Results
    if submitted:
        if not video_input:
            st.error("🚨 Please enter a YouTube URL or Video ID!")
        else:
            video_id = extract_video_id(video_input)
            if not video_id:
                st.error("❌ Invalid YouTube URL or Video ID format. Please check your input.")
            else:
                # Processing section with step indicator
                st.markdown("""
                <div class="step-indicator">
                    <div class="step active">1</div>
                    <div class="step">2</div>
                    <div class="step">3</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="status-container">', unsafe_allow_html=True)
                with st.status("🤖 **AI Agents are processing your video...**", state="running", expanded=True) as status:
                    st.markdown("**📺 Transcript Agent** - Extracting video transcript")
                    st.markdown("**📋 Summary Agent** - Creating blog outline")
                    st.markdown("**✍️ Blog Writer Agent** - Writing engaging content")
                    
                    # Progress container
                    progress_container = st.container()
                    with progress_container:
                        progress_bar = st.progress(0)
                        progress_text = st.empty()
                        
                        # Simulate progress updates
                        progress_bar.progress(25)
                        progress_text.text("Extracting transcript...")
                        
                        # Run the blog creation process
                        blog_crew = BlogCrew(video_id)
                        
                        progress_bar.progress(50)
                        progress_text.text("Analyzing content...")
                        
                        result = blog_crew.run()
                        
                        progress_bar.progress(75)
                        progress_text.text("Writing blog post...")
                        
                        progress_bar.progress(100)
                        progress_text.text("Complete!")
                    
                    # Update step indicator
                    st.markdown("""
                    <div class="step-indicator">
                        <div class="step completed">1</div>
                        <div class="step completed">2</div>
                        <div class="step completed">3</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    status.update(label="✅ Your blog post is ready!", state="complete", expanded=False)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Results section
                if result:
                    st.markdown('<div class="results-container">', unsafe_allow_html=True)
                    st.markdown("## 📝 Your Generated Blog Post")
                    st.markdown("---")
                    
                    # Display the blog post
                    st.markdown(result.raw if hasattr(result, 'raw') else str(result))
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Download and sharing options
                    col_download1, col_download2, col_download3 = st.columns(3)
                    
                    with col_download1:
                        st.download_button(
                            label="📄 Download as Markdown",
                            data=result.raw if hasattr(result, 'raw') else str(result),
                            file_name=f"blog_post_{video_id}_{datetime.datetime.now().strftime('%Y%m%d')}.md",
                            mime="text/markdown"
                        )
                    
                    with col_download2:
                        st.download_button(
                            label="📋 Download as Text",
                            data=result.raw if hasattr(result, 'raw') else str(result),
                            file_name=f"blog_post_{video_id}_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )
                    
                    with col_download3:
                        if st.button("🔗 Copy to Clipboard"):
                            st.code(result.raw if hasattr(result, 'raw') else str(result))

    # Usage Instructions
    with st.expander("📖 How to Use YT2Blog", expanded=False):
        st.markdown("""
        ### Step-by-Step Guide:
        
        1. **Find Your Video**: Copy the URL of any YouTube video you want to convert
        2. **Paste the Link**: Enter the URL or just the video ID in the input field above
        3. **Choose Options**: Select your preferred writing style and additional options
        4. **Generate**: Click the "Generate Blog Post" button and wait for the AI to work its magic
        5. **Download**: Save your blog post in markdown or text format
        
        ### Supported URL Formats:
        - `https://www.youtube.com/watch?v=VIDEO_ID`
        - `https://youtu.be/VIDEO_ID`
        - `https://www.youtube.com/embed/VIDEO_ID`
        - Direct Video ID: `VIDEO_ID`
        
        ### Tips for Better Results:
        - Choose videos with clear audio and good speech quality
        - Longer videos (10+ minutes) tend to produce more comprehensive blog posts
        - Educational and tutorial videos work exceptionally well
        """)

    # Footer with credits
    st.markdown("---")
    st.markdown("""
    <div class="credits-container">
        <h3>🙏 Built with Cutting-Edge AI</h3>
        <p>Powered by <strong>CrewAI</strong>, <strong>Google Gemini</strong>, and <strong>YouTube Transcript API</strong></p>
        <p>Created with ❤️ for content creators and bloggers worldwide</p>
        <p><em>Transform any YouTube video into engaging, SEO-optimized blog content in minutes!</em></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()