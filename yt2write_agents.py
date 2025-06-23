import logging
from crewai import Agent, LLM
from tools.youtube_transcript_extraction import YoutubeTranscriptTool
from tools.email_tool import SendEmailTool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

class YT2WriteAgents():
    """
    A class to manage different AI agents for YouTube transcript extraction,
    summarization, and blog writing.
    """

    def __init__(self):
        """
        Initialize the TripAgents class with LLM and YoutubeTranscriptTool.
        """
        logger.info("Initializing TripAgents...")
        self.llm = LLM(model="gemini/gemini-2.5-flash")
        self.youtube_tool = YoutubeTranscriptTool()
        self.email_tool = SendEmailTool()
        logger.info("TripAgents initialized successfully.")

    def transcript_agent(self):
        """
        Create an agent specialized in extracting and formatting YouTube transcripts.
        """
        logger.info("Creating Transcript Extraction Specialist agent.")
        return Agent(
            role="Transcript Extraction Specialist",
            goal="Retrieve a clean and accurate transcript from a Youtube video using the video ID",
            backstory=(
                "You are a highly skilled agent with expertise in extracting and formatting transcripts from online video content. "
                "Your main responsibility is to process YouTube videos and return the entire transcript in a clean, readable format "
                "so it can be used to generate high-quality blog posts."
            ),
            tools=[self.youtube_tool],
            allow_delegation=False,
            llm=self.llm
        )

    def summary_agent(self):
        """
        Create an agent that summarizes transcripts and generates blog outlines.
        """
        logger.info("Creating Blog Outline Strategist agent.")
        return Agent(
            role="Blog Outline Strategist",
            goal="Summarize the video transcript and generate a clear, structured outline suitable for a blog post.",
            backstory=(
                "You are a content strategist and summarization expert. "
                "Your job is to convert long-form transcripts into concise outlines that form the structure of engaging blog posts. "
                "You identify key points, themes, and subtopics that can be expanded into full sections."
            ),
            llm=self.llm,
            allow_delegation=False
        )

    def blog_writer_agent(self):
        """
        Create an agent that writes SEO-friendly blog posts from outlines and transcripts.
        """
        logger.info("Creating AI Blog Writer agent.")
        return Agent(
            role="AI Blog Writer",
            goal="Write an engaging, SEO-friendly blog post based on the provided outline and transcript.",
            backstory=(
                "You are a skilled blog writer who specializes in converting outlines and transcripts into full-length, readable blog articles. "
                "You maintain a conversational tone, ensure readability, and make the blog informative yet engaging."
            ),
            llm=self.llm,
            allow_delegation=False
        )
    
    def email_agent(self):
        """
        Create an agent that sends blog posts via email.
        """
        logger.info("Creating Email Delivery Specialist agent.")
        return Agent(
            role="Email Delivery Specialist",
            goal="Send the completed blog post to the specified recipient via email with proper formatting and subject line.",
            backstory=(
                "You are a professional email communication specialist. "
                "Your role is to deliver completed blog posts to users via email with appropriate subject lines "
                "and professional formatting. You ensure the content is properly presented and easy to read."
            ),
            tools=[self.email_tool],
            llm=self.llm,
            allow_delegation=False
        )