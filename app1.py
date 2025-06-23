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
    background: #ffffff;
    color: #333333;
}

.stTextInput > div > div > input::placeholder {
    color: #888888;
    opacity: 1;
}

.stTextInput > div > div > input:focus {
    outline: none;
    border-color: #4285f4;
    box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.1);
}
    
    /* Email input special styling */
    .email-input {
        background: linear-gradient(135deg, #f8f9ff 0%, #e6f3ff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #2196f3;
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
    
    /* Checkbox styling */
    .stCheckbox > label {
        font-size: 1.1rem;
        font-weight: 500;
        color: #333;
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
    
    /* Email preview styling */
    .email-preview {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #4caf50;
    }
    
    .email-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2e7d32;
        margin-bottom: 0.5rem;
    }
    
    .email-address {
        font-family: 'Courier New', monospace;
        background: rgba(255,255,255,0.7);
        padding: 0.5rem;
        border-radius: 8px;
        color: #1b5e20;
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
    
    /* Warning box */
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    
    /* Success message styling */
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
        color: #155724;
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


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


class BlogCrew:
    def __init__(self, video_id, email_address=None):
        self.video_id = video_id
        self.email_address = email_address
        self.output_placeholder = st.empty()
        self.llm = LLM(model="gemini/gemini-2.0-flash")

    def run(self):
        """
        Run the blog creation process with proper task dependencies
        to ensure blog content is always returned for display
        """
        try:
            # Initialize agents and tasks
            agents = YT2WriteAgents()
            tasks = YT2WriteTasks()

            # Create agents
            transcript_agent = agents.transcript_agent()
            summary_agent = agents.summary_agent()
            blog_writer_agent = agents.blog_writer_agent()

            logger.info("Agents assigned")

            # Create core tasks with proper dependencies
            extract_task = tasks.extract_transcript_text(transcript_agent, self.video_id)
            outline_task = tasks.outline_task(summary_agent)
            blog_task = tasks.write_blog(blog_writer_agent)

            # Create crew with core tasks
            crew_agents = [transcript_agent, summary_agent, blog_writer_agent]
            crew_tasks = [extract_task, outline_task, blog_task]

            logger.info("Core tasks assigned")

            # Create and run crew for blog generation
            crew = Crew(
                agents=crew_agents,
                tasks=crew_tasks,
                verbose=True
            )

            logger.info("Executing blog generation crew")
            blog_result = crew.kickoff()
            
            # Extract the blog content from the result
            blog_content = blog_result.raw if hasattr(blog_result, 'raw') else str(blog_result)
            
            # If email is requested, send it separately but still return the blog content
            if self.email_address:
                try:
                    logger.info("Sending email with blog content")
                    email_agent = agents.email_agent()
                    email_task = tasks.send_blog_email(
                        email_agent, 
                        self.email_address, 
                        f"YouTube Video {self.video_id}"
                    )
                    
                    crew_agents.append(email_agent)
                    crew_tasks.append(email_task)

                    # Create a separate crew just for email sending
                    email_crew = Crew(
                        agents=crew_agents,
                        tasks=crew_tasks,
                        verbose=True
                    )
                    
                   
                    # Execute email sending
                    email_result = email_crew.kickoff()
                    logger.info("Email sent successfully")
                    
                    # Return the blog content with email confirmation
                    return {
                        'blog_content': blog_content,
                        'email_sent': True,
                        'email_address': self.email_address
                    }
                    
                except Exception as email_error:
                    logger.error(f"Email sending failed: {email_error}")
                    # Even if email fails, return the blog content
                    return {
                        'blog_content': blog_content,
                        'email_sent': False,
                        'email_error': str(email_error)
                    }
            
            # Return just the blog content if no email requested
            return {
                'blog_content': blog_content,
                'email_sent': False
            }
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logger.error(f"Blog creation failed: {e}")
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
            "📧", 
            "Email Delivery",
            "Get your blog post delivered directly to your inbox automatically"
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
                    help="Paste a YouTube URL or enter the video ID directly",
                    key="video_input"
                )
                
                # Email delivery section
                st.markdown("#### 📧 Email Delivery (Optional)")
                
                # Checkbox to enable email delivery
                send_email = st.checkbox(
                    "📮 Send blog post to my email",
                    help="Check this to receive the generated blog post via email"
                )
                
                # Email input field (only shown if checkbox is checked)
                email_address = None
                if send_email:
                    st.markdown('<div class="email-input">', unsafe_allow_html=True)
                    email_address = st.text_input(
                        "Your Email Address:",
                        placeholder="your.email@example.com",
                        help="Enter your email address to receive the blog post",
                        key="email_input"
                    )
                    
                    # Validate email format if provided
                    if email_address and not validate_email(email_address):
                        st.error("❌ Please enter a valid email address")
                    elif email_address and validate_email(email_address):
                        st.markdown(f"""
                        <div class="email-preview">
                            <div class="email-title">✅ Email Delivery Enabled</div>
                            <div class="email-address">Blog will be sent to: {email_address}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                
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
                    button_text = "🚀 Generate & Send Blog Post" if send_email else "🚀 Generate Blog Post"
                    submitted = st.form_submit_button(button_text, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Processing and Results
    if submitted:
        if not video_input:
            st.error("🚨 Please enter a YouTube URL or Video ID!")
        elif send_email and not email_address:
            st.error("🚨 Please enter your email address or uncheck the email delivery option!")
        elif send_email and email_address and not validate_email(email_address):
            st.error("🚨 Please enter a valid email address!")
        else:
            video_id = extract_video_id(video_input)
            if not video_id:
                st.error("❌ Invalid YouTube URL or Video ID format. Please check your input.")
            else:
                # Processing section with step indicator
                step_count = 4 if send_email else 3
                steps_html = ""
                for i in range(1, step_count + 1):
                    if i == 1:
                        steps_html += f'<div class="step active">{i}</div>'
                    else:
                        steps_html += f'<div class="step">{i}</div>'
                
                st.markdown(f"""
                <div class="step-indicator">
                    {steps_html}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="status-container">', unsafe_allow_html=True)
                
                status_text = "🤖 **AI Agents are processing your video...**"
                if send_email:
                    status_text += " and preparing email delivery"
                
                with st.status(status_text, state="running", expanded=True) as status:
                    st.markdown("**📺 Transcript Agent** - Extracting video transcript")
                    st.markdown("**📋 Summary Agent** - Creating blog outline")
                    st.markdown("**✍️ Blog Writer Agent** - Writing engaging content")
                    if send_email:
                        st.markdown("**📧 Email Agent** - Preparing email delivery")
                    
                    # Progress container
                    progress_container = st.container()
                    with progress_container:
                        progress_bar = st.progress(0)
                        progress_text = st.empty()
                        
                        # Simulate progress updates
                        progress_bar.progress(25)
                        progress_text.text("Extracting transcript...")
                        
                        # Run the blog creation process
                        final_email = email_address if send_email and validate_email(email_address) else None
                        blog_crew = BlogCrew(video_id, final_email)
                        
                        progress_bar.progress(50)
                        progress_text.text("Analyzing content...")
                        
                        result = blog_crew.run()
                        
                        progress_bar.progress(75)
                        progress_text.text("Writing blog post...")
                        
                        if send_email and final_email:
                            progress_bar.progress(90)
                            progress_text.text("Sending email...")
                        
                        progress_bar.progress(100)
                        progress_text.text("Complete!")
                    
                    # Update step indicator to show completion
                    completed_steps_html = ""
                    for i in range(1, step_count + 1):
                        completed_steps_html += f'<div class="step completed">{i}</div>'
                    
                    st.markdown(f"""
                    <div class="step-indicator">
                        {completed_steps_html}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    success_message = "✅ Your blog post is ready!"
                    if send_email and final_email:
                        success_message += f" Email delivery attempted."
                    
                    status.update(label=success_message, state="complete", expanded=False)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Results section - Always show the blog content
                if result and isinstance(result, dict) and 'blog_content' in result:
                    st.markdown('<div class="results-container">', unsafe_allow_html=True)
                    st.markdown("## 📝 Your Generated Blog Post")
                    
                    # Email status messages
                    if result.get('email_sent'):
                        st.markdown(f"""
                        <div class="success-message">
                            <strong>📧 Success!</strong> Blog post has been sent to: <strong>{result.get('email_address')}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    elif 'email_error' in result:
                        st.warning(f"📧 Email delivery failed: {result['email_error']}")
                        st.info("Don't worry! Your blog post is still ready below. You can copy or download it.")
                    
                    st.markdown("---")
                    
                    # Display the blog post content
                    blog_content = result['blog_content']
                    st.markdown(blog_content)
                    
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
        3. **Choose Email Delivery** (Optional): Check the box and enter your email to receive the blog post
        4. **Generate**: Click the "Generate Blog Post" button and wait for the AI to work its magic
        5. **Download or Receive**: Save your blog post or check your email if delivery was enabled
        
        ### Supported URL Formats:
        - `https://www.youtube.com/watch?v=VIDEO_ID`
        - `https://youtu.be/VIDEO_ID`
        - `https://www.youtube.com/embed/VIDEO_ID`
        - Direct Video ID: `VIDEO_ID`
        
        ### Email Delivery Setup:
        - Make sure `EMAIL_ADDRESS` and `EMAIL_PASSWORD` environment variables are configured
        - Uses Gmail SMTP by default (smtp.gmail.com:587)
        - Email includes the full blog post with professional formatting
        
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