from crewai import Task
from dotenv import load_dotenv

load_dotenv()

class YT2WriteTasks():
    
    def __init__(self):
        """Initialize the tasks class"""
        pass
    
    def extract_transcript_text(self, agent, video_id):
        """Extract transcript task that accepts video_id as parameter"""
        return Task(
            description=f"Extract transcript for video ID '{video_id}'. Use the YouTube transcript tool to fetch the complete transcript.",
            expected_output="Full transcript text from the YouTube video.",
            agent=agent
        )
    
    def outline_task(self, agent):
        """Create blog outline from transcript"""
        return Task(
            description="Create a detailed outline suitable for a blog post from the transcript. Analyze the transcript content and create a structured outline with main headings and subheadings that will form the skeleton of an engaging blog post.",
            expected_output="A structured blog outline with clear headings, subheadings, and key points that can be expanded into full sections.",
            agent=agent
        )
    
    def write_blog(self, agent):
        """Write complete blog post from outline"""
        return Task(
            description="Write a full blog article from the outline and transcript content. Create an engaging, SEO-friendly blog post with proper formatting, clear sections, and conversational tone. Include an introduction, main content sections based on the outline, and a conclusion.",
            expected_output="Complete blog article in markdown format with proper headings, engaging content, and SEO-friendly structure.",
            agent=agent
        )