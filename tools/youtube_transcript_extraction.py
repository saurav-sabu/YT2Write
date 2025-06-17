import logging
from crewai.tools import BaseTool
from youtube_transcript_api import YouTubeTranscriptApi
from pydantic import BaseModel, Field

# Set up a basic logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class TranscriptInput(BaseModel):
    video_id: str = Field(..., description="The youtube video ID")  # Corrected typo in 'description'

class YoutubeTranscriptTool(BaseTool):
    name: str = "Youtube Transcript Tool"
    description: str = "Fetches and formats transcript from a Youtube Video using its video ID"
    args_schema: type[BaseModel] = TranscriptInput

    def _run(self, video_id: str):
        """
        Fetches the transcript for a given YouTube video ID and returns it as a single string.
        Args:
            video_id (str): The YouTube video ID.
        Returns:
            str: The concatenated transcript text or an error message.
        """
        try:
            logger.info(f"Fetching transcript for video ID: {video_id}")
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            # Join all transcript segments into a single string
            transcript_text = " ".join([t["text"] for t in transcript])
            logger.info("Transcript fetched successfully.")
            return transcript_text
        except Exception as e:
            logger.error(f"Failed to fetch the transcript: {str(e)}")
            return f"Failed to fetch the transcript: {str(e)}"